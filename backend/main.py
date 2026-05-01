from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from parser import extract_text_from_pdf, extract_sections
from scorer import calculate_match_score

# Create the FastAPI app
app = FastAPI(
    title="TalentTrace API",
    description="AI-Powered Resume Screener Backend",
    version="1.0.0"
)

# Allow frontend to talk to backend later (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary folder to store uploaded PDFs
UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Welcome to TalentTrace API 🚀"}


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts a PDF resume, extracts and returns the text.
    """

    # 1. Check if uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # 2. Save the file temporarily with a unique name
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Extract text from the saved PDF
    try:
        extracted_text = extract_text_from_pdf(file_path)
        sections = extract_sections(extracted_text)
    except Exception as e:
        os.remove(file_path)  # Clean up on error
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

    # 4. Delete the temp file after extraction
    os.remove(file_path)

    # 5. Return the extracted data as JSON
    return {
        "filename": file.filename,
        "full_text": extracted_text,
        "sections": sections,
        "character_count": len(extracted_text),
        "word_count": len(extracted_text.split())
    }

@app.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Accepts a resume PDF + job description text.
    Returns match score, matched skills, missing skills, and suggestions.
    """

    # 1. Validate file
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # 2. Save temporarily
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Extract resume text
    try:
        resume_text = extract_text_from_pdf(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")

    # 4. Clean up temp file
    os.remove(file_path)

    # 5. Calculate match score
    result = calculate_match_score(resume_text, job_description)

    return {
        "filename": file.filename,
        "job_description_preview": job_description[:200] + "...",
        "match_score": result["match_score"],
        "skill_score": result["skill_score"],
        "semantic_score": result["semantic_score"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "total_jd_skills": result["total_jd_skills"],
        "total_resume_skills": result["total_resume_skills"],
        "suggestions": result["suggestions"],
        "ats_score": result["ats_score"],
        "ats_warnings": result["ats_warnings"],
        "experience_level": result["experience_level"],
    }