from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from pathlib import Path


app = FastAPI(title="AskMyNotes API")


# ==========================================
# CORS
# ==========================================

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Local Vite can sometimes use another port
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "https://askmynotes-real-frontend.onrender.com",

    # Add your actual Render frontend URL here
    # "https://your-frontend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Upload folder
# ==========================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# Request model
# ==========================================

class QuestionRequest(BaseModel):
    question: str


# ==========================================
# Home
# ==========================================

@app.get("/")
def home():
    return {
        "message": "AskMyNotes backend is running"
    }


# ==========================================
# Health
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ==========================================
# Upload PDF
# ==========================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Prevent unsafe filenames
    safe_filename = Path(file.filename).name

    file_path = os.path.join(
        UPLOAD_FOLDER,
        safe_filename
    )

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        print("Starting PDF processing...")

        # Import only when upload is requested
        from rag import process_pdf

        result = process_pdf(file_path)

        print("PDF processed successfully.")

        return {
            "message": "PDF uploaded and processed successfully",
            "filename": safe_filename,
            "chunks": result["chunks"]
        }

    except Exception as e:

        print("ERROR IN /upload:")
        print(repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================
# Ask Question
# ==========================================

@app.post("/ask")
async def ask(request: QuestionRequest):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        print("ASK endpoint called")
        print("Question:", request.question)

        # Import only when question is requested
        from rag import ask_question

        result = await ask_question(
            request.question
        )

        print("Answer generated successfully.")

        return result

    except Exception as e:

        print("ERROR IN /ask:")
        print(repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )