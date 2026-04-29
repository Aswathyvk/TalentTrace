from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from parser import extract_text_from_pdf, extract_sections

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