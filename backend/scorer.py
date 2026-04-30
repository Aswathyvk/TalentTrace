from sentence_transformers import SentenceTransformer, util
import spacy

nlp = spacy.load("en_core_web_md")
model = SentenceTransformer("all-MiniLM-L6-v2")

SKILL_KEYWORDS = [
    "python", "java", "javascript", "react", "node", "sql", "machine learning",
    "deep learning", "tensorflow", "pytorch", "docker", "kubernetes", "aws",
    "fastapi", "django", "flask", "git", "linux", "nlp", "data analysis",
    "pandas", "numpy", "scikit-learn", "html", "css", "mongodb", "postgresql"
]

def extract_skills(text: str) -> list:
    text_lower = text.lower()
    return [skill for skill in SKILL_KEYWORDS if skill in text_lower]

def compute_match_score(resume_text: str, jd_text: str) -> dict:
    # Semantic score
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    semantic_score = round(util.cos_sim(resume_emb, jd_emb).item() * 100, 2)

    # Skill score
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))
    matched_skills = list(resume_skills & jd_skills)
    missing_skills = list(jd_skills - resume_skills)
    skill_score = round((len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0, 2)

    # Overall match score
    match_score = round((semantic_score * 0.5) + (skill_score * 0.5), 2)

    # Suggestions
    suggestions = []
    for skill in missing_skills:
        suggestions.append(f"Add '{skill}' to your resume — it is required in the job description.")
    if match_score < 50:
        suggestions.append("Your resume needs significant improvement to match this job.")
    elif match_score < 75:
        suggestions.append("You are a moderate match. Focus on adding the missing skills.")
    else:
        suggestions.append("Great match! You are a strong candidate for this role.")

    return {
        "match_score": match_score,
        "skill_score": skill_score,
        "semantic_score": semantic_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_jd_skills": len(jd_skills),
        "total_resume_skills": len(resume_skills),
        "suggestions": suggestions
    }