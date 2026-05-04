# TalentTrace 🎯
AI-Powered Resume Screener & Job Match Analyzer

## 🚀 Live Demo
- Frontend: (coming soon - Vercel)
- Backend API: (coming soon - Render)

## 🛠️ Tech Stack
- **Backend:** Python, FastAPI
- **NLP:** spaCy, sentence-transformers
- **ML:** scikit-learn
- **Frontend:** React, Recharts
- **PDF Parsing:** pdfplumber

## ✨ Features
- 📄 PDF resume upload and text extraction
- 🤖 AI-powered resume vs job description matching
- 📊 Match score, skill score, semantic score
- 🔍 Skill gap analysis (matched vs missing skills)
- 🤖 ATS compatibility score
- 💡 Improvement suggestions
- 📈 Visual score breakdown charts
- 🎯 Experience level detection (Fresher/Mid/Senior)

## 🏃 Run Locally

### Backend
```bash
cd backend
uvicorn main:app --reload
```
Visit http://localhost:8000/docs

### Frontend
```bash
cd frontend/talenttrace-ui
npm start
```
Visit http://localhost:3000
