# # from rag import process_pdf, ask_question
# # from fastapi import FastAPI, UploadFile, File, HTTPException
# # from fastapi.middleware.cors import CORSMiddleware
# # from pydantic import BaseModel
# # import os
# # import shutil

# # app = FastAPI(title="AskMyNotes API")

# # allow_origins=[
# #        "https://askmynotes-frontend-r1w6.onrender.com",  # confirm this is the exact live URL, no trailing "/"
# #        "http://localhost:5173",
# #        "http://127.0.0.1:5173",
# #    ],

# # UPLOAD_FOLDER = "uploads"

# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# # class QuestionRequest(BaseModel):
# #     question: str


# # @app.get("/")
# # def home():
# #     return {
# #         "message": "AskMyNotes backend is running"
# #     }


# # @app.get("/health")
# # def health():
# #     return {
# #         "status": "healthy"
# #     }

# # @app.post("/upload")
# # async def upload_pdf(file: UploadFile = File(...)):

# #     if not file.filename.lower().endswith(".pdf"):
# #         raise HTTPException(
# #             status_code=400,
# #             detail="Only PDF files are allowed."
# #         )

# #     file_path = os.path.join(UPLOAD_FOLDER, file.filename)

# #     with open(file_path, "wb") as buffer:
# #         shutil.copyfileobj(file.file, buffer)

# #     try:
# #         result = process_pdf(file_path)

# #         return {
# #         "message": "PDF uploaded and processed successfully",
# #         "filename": file.filename,
# #         "chunks": result["chunks"]
# #         }

# #     except Exception as e:
# #        raise HTTPException(
# #         status_code=500,
# #         detail=str(e)
# #         )
    
# # @app.post("/ask")
# # async def ask(request: QuestionRequest):
# #     try:
# #         print("ASK endpoint called")
# #         print("Question:", request.question)

# #         result = await ask_question(request.question)

# #         print("Answer generated successfully")

# #         return result

# #     except Exception as e:
# #         print("ERROR IN /ask:")
# #         print(repr(e))

# #         raise HTTPException(
# #             status_code=500,
# #             detail=str(e)
# #         )

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import os
# import shutil

# from rag import process_pdf, ask_question

# app = FastAPI(title="AskMyNotes API")

# # ✅ CORS MIDDLEWARE — must be added right after app is created
# origins = [
#     "http://localhost:5173",
#     "http://localhost:5174",
#     "http://localhost:5175",
#     "http://127.0.0.1:5173",
#     "http://127.0.0.1:5174",
#     "http://127.0.0.1:5175",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# class QuestionRequest(BaseModel):
#     question: str


# @app.get("/")
# def home():
#     return {"message": "AskMyNotes backend is running"}


# @app.get("/health")
# def health():
#     return {"status": "healthy"}


# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...)):
#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     try:
#         result = process_pdf(file_path)
#         return {
#             "message": "PDF uploaded and processed successfully",
#             "filename": file.filename,
#             "chunks": result["chunks"],
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/ask")
# async def ask(request: QuestionRequest):
#     try:
#         result = await ask_question(request.question)
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

app = FastAPI(title="AskMyNotes API")


# ==========================================
# CORS
# ==========================================

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Add your Render frontend URL here later
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
# Health check
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

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        print("Processing PDF...")

        # Import RAG only when /upload is called
        from rag import process_pdf

        result = process_pdf(file_path)

        print("PDF processed successfully.")

        return {
            "message": "PDF uploaded and processed successfully",
            "filename": file.filename,
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
# Ask question
# ==========================================

@app.post("/ask")
async def ask(request: QuestionRequest):

    try:

        print("ASK endpoint called")
        print("Question:", request.question)

        # Import RAG only when /ask is called
        from rag import ask_question

        result = await ask_question(
            request.question
        )

        print("Answer generated successfully")

        return result

    except Exception as e:

        print("ERROR IN /ask:")
        print(repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )