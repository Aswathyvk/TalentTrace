import pdfplumber
import re

def extract_text_from_pdf(file_path: str) -> str:
    """
    Takes a PDF file path and returns clean extracted text.
    """
    full_text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"

    cleaned_text = clean_text(full_text)
    return cleaned_text


def clean_text(text: str) -> str:
    """
    Cleans up the raw extracted text.
    """
    # Remove extra whitespace and blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Remove weird characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove extra spaces
    text = re.sub(r' +', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def extract_sections(text: str) -> dict:
    """
    Tries to identify common resume sections.
    """
    sections = {
        "education": "",
        "experience": "",
        "skills": "",
        "projects": "",
        "other": ""
    }

    # Keywords to detect each section
    section_keywords = {
        "education": ["education", "academic", "qualification"],
        "experience": ["experience", "employment", "work history", "internship"],
        "skills": ["skills", "technical skills", "technologies", "tools"],
        "projects": ["projects", "personal projects", "academic projects"],
    }

    lines = text.split('\n')
    current_section = "other"

    for line in lines:
        line_lower = line.lower().strip()

        # Check if this line is a section header
        matched = False
        for section, keywords in section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                current_section = section
                matched = True
                break

        sections[current_section] += line + "\n"

    return sections


# ---- TEST IT HERE ----
if __name__ == "__main__":
    # Put your resume PDF path here
    pdf_path = "resume.pdf"

    print("=== EXTRACTING TEXT ===")
    text = extract_text_from_pdf(pdf_path)
    print(text)

    print("\n=== SECTIONS DETECTED ===")
    sections = extract_sections(text)
    for section, content in sections.items():
        if content.strip():
            print(f"\n--- {section.upper()} ---")
            print(content[:300])  # Print first 300 chars of each section