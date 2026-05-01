import spacy
from sentence_transformers import SentenceTransformer, util
import re

# Load models
nlp = spacy.load("en_core_web_md")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Expanded skills list
SKILLS_LIST = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "r", "golang", "rust", "kotlin", "swift", "php", "ruby", "scala",

    # AI / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "artificial intelligence", "ai", "ml",
    "tensorflow", "pytorch", "keras", "scikit-learn", "opencv",
    "huggingface", "transformers", "bert", "gpt", "llm",
    "reinforcement learning", "neural network",

    # Data
    "data analysis", "data science", "data engineering", "data visualization",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "power bi", "tableau", "excel", "statistics",

    # Web
    "react", "angular", "vue", "next.js", "node.js",
    "django", "fastapi", "flask", "spring boot", "express",
    "html", "css", "tailwind", "bootstrap", "rest api", "graphql",

    # Mobile
    "android", "ios", "flutter", "react native", "kotlin", "swift",

    # Databases
    "mysql", "postgresql", "mongodb", "firebase", "sqlite",
    "redis", "elasticsearch", "oracle", "sql", "nosql",

    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "ci/cd", "jenkins", "github actions", "terraform", "linux",

    # Tools
    "git", "github", "gitlab", "jira", "figma", "postman",
    "vs code", "jupyter", "anaconda",

    # Soft Skills
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "agile", "scrum",
]

# ATS keywords that recruiters look for
ATS_KEYWORDS = [
    "experience", "project", "developed", "built", "designed",
    "implemented", "managed", "led", "achieved", "improved",
    "bachelor", "master", "degree", "certified", "certification",
    "team", "collaborate", "responsible", "result", "impact",
]


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_LIST:
        if skill in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))


def calculate_ats_score(resume_text: str) -> dict:
    """
    Checks how ATS-friendly the resume is.
    """
    text_lower = resume_text.lower()
    found_keywords = [kw for kw in ATS_KEYWORDS if kw in text_lower]
    ats_score = round((len(found_keywords) / len(ATS_KEYWORDS)) * 100, 1)

    # Check formatting red flags
    warnings = []
    if len(resume_text) < 300:
        warnings.append("Resume seems too short.")
    if "@" not in resume_text:
        warnings.append("No email address detected.")
    if not any(char.isdigit() for char in resume_text):
        warnings.append("No numbers found — add measurable achievements.")

    return {
        "ats_score": ats_score,
        "found_ats_keywords": found_keywords,
        "ats_warnings": warnings
    }

def detect_experience_level(resume_text: str) -> str:
    text_lower = resume_text.lower()

    senior_keywords = ["senior", "lead engineer", "tech lead",
                       "architect", "head of", "principal", "director"]
    mid_keywords = ["3 years", "4 years", "5 years", "3+ years",
                    "4+ years", "mid-level", "intermediate"]
    fresher_keywords = ["fresher", "fresh graduate", "entry level",
                        "0-1 year", "1 year experience", "recent graduate",
                        "mca", "b.tech", "btech", "pursuing", "completed"]

    # Count matches for each level
    senior_count = sum(1 for kw in senior_keywords if kw in text_lower)
    mid_count = sum(1 for kw in mid_keywords if kw in text_lower)
    fresher_count = sum(1 for kw in fresher_keywords if kw in text_lower)

    # Fresher takes priority if MCA/BTech detected
    if fresher_count >= 1 and senior_count <= 1:
        return "Entry Level / Fresher"
    elif senior_count > mid_count and senior_count > fresher_count:
        return "Senior Level"
    elif mid_count > 0:
        return "Mid Level"
    else:
        return "Entry Level / Fresher"


def calculate_match_score(resume_text: str, job_description: str) -> dict:
    """
    Full analysis — match score, skill gap, ATS, experience level.
    """
    # 1. Extract skills
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    # 2. Matched and missing
    matched_skills = [s for s in jd_skills if s in resume_skills]
    missing_skills = [s for s in jd_skills if s not in resume_skills]

    # 3. Skill score
    skill_score = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0

    # 4. Semantic similarity
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(job_description, convert_to_tensor=True)
    semantic_score = float(util.cos_sim(resume_embedding, jd_embedding)[0][0]) * 100

    # 5. Final score
    final_score = round((skill_score * 0.5) + (semantic_score * 0.5), 1)

    # 6. ATS analysis
    ats_data = calculate_ats_score(resume_text)

    # 7. Experience level
    experience_level = detect_experience_level(resume_text)

    # 8. Suggestions
    suggestions = generate_suggestions(missing_skills, ats_data["ats_warnings"])

    return {
        "match_score": final_score,
        "skill_score": round(skill_score, 1),
        "semantic_score": round(semantic_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_jd_skills": len(jd_skills),
        "total_resume_skills": len(resume_skills),
        "ats_score": ats_data["ats_score"],
        "ats_warnings": ats_data["ats_warnings"],
        "experience_level": experience_level,
        "suggestions": suggestions
    }


def generate_suggestions(missing_skills: list, ats_warnings: list) -> list:
    suggestions = []

    if not missing_skills:
        suggestions.append("Great match! Your resume covers all key skills.")
        return suggestions

    ml_skills = ["machine learning", "deep learning", "tensorflow",
                 "pytorch", "keras", "scikit-learn", "nlp", "computer vision"]
    web_skills = ["react", "angular", "vue", "node.js",
                  "django", "fastapi", "flask", "html", "css"]
    db_skills = ["mysql", "postgresql", "mongodb", "firebase", "sql"]
    cloud_skills = ["aws", "azure", "gcp", "docker", "kubernetes"]

    missing_ml = [s for s in missing_skills if s in ml_skills]
    missing_web = [s for s in missing_skills if s in web_skills]
    missing_db = [s for s in missing_skills if s in db_skills]
    missing_cloud = [s for s in missing_skills if s in cloud_skills]

    if missing_ml:
        suggestions.append(f"Add ML/AI skills: {', '.join(missing_ml)}")
    if missing_web:
        suggestions.append(f"Mention web technologies: {', '.join(missing_web)}")
    if missing_db:
        suggestions.append(f"Include database experience: {', '.join(missing_db)}")
    if missing_cloud:
        suggestions.append(f"Consider adding cloud skills: {', '.join(missing_cloud)}")
    if ats_warnings:
        suggestions.extend(ats_warnings)
    if len(missing_skills) > 5:
        suggestions.append("Tailor your resume specifically for this job description.")

    return suggestions


# ---- TEST ----
if __name__ == "__main__":
    sample_resume = """
    Abhishek - MCA Graduate
    Email: abhishek@email.com
    Developed a Landslide Prediction System using Python, Machine Learning,
    TensorFlow, and satellite imagery. Built REST API using FastAPI.
    Worked with PostgreSQL, Git, and collaborated with a team of 3.
    Achieved 92% accuracy in the prediction model. Strong communication skills.
    """

    sample_jd = """
    Looking for a Python Developer with experience in machine learning,
    NLP, React, PostgreSQL, Docker, and AWS. Must have good communication skills
    and experience building REST APIs.
    """

    result = calculate_match_score(sample_resume, sample_jd)
    print(f"Match Score:      {result['match_score']}%")
    print(f"Skill Score:      {result['skill_score']}%")
    print(f"Semantic Score:   {result['semantic_score']}%")
    print(f"ATS Score:        {result['ats_score']}%")
    print(f"Experience Level: {result['experience_level']}")
    print(f"Matched Skills:   {result['matched_skills']}")
    print(f"Missing Skills:   {result['missing_skills']}")
    print(f"Suggestions:      {result['suggestions']}")