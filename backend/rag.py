# # import os
# # import numpy as np
# # from pypdf import PdfReader
# # from sentence_transformers import SentenceTransformer
# # import httpx


# # # Load embedding model
# # embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# # # Store the current PDF data in memory
# # chunks = []
# # chunk_embeddings = []


# # def extract_text_from_pdf(pdf_path):
# #     """Extract text from the uploaded PDF."""

# #     reader = PdfReader(pdf_path)

# #     text = ""

# #     for page in reader.pages:
# #         page_text = page.extract_text()

# #         if page_text:
# #             text += page_text + "\n"

# #     return text


# # def create_chunks(text, chunk_size=500, overlap=100):
# #     """Split PDF text into smaller chunks."""

# #     words = text.split()

# #     result = []

# #     start = 0

# #     while start < len(words):

# #         end = start + chunk_size

# #         chunk = " ".join(words[start:end])

# #         if chunk.strip():
# #             result.append(chunk)

# #         start += chunk_size - overlap

# #     return result


# # def create_embeddings(text_chunks):
# #     """Convert text chunks into numerical vectors."""

# #     embeddings = embedding_model.encode(
# #         text_chunks,
# #         convert_to_numpy=True
# #     )

# #     return embeddings


# # def process_pdf(pdf_path):
# #     """
# #     Read the PDF, split it into chunks,
# #     and create embeddings.
# #     """

# #     global chunks
# #     global chunk_embeddings

# #     text = extract_text_from_pdf(pdf_path)

# #     if not text.strip():
# #         raise ValueError("No readable text found in the PDF.")

# #     chunks = create_chunks(text)

# #     chunk_embeddings = create_embeddings(chunks)

# #     return {
# #         "chunks": len(chunks),
# #         "message": "PDF processed successfully"
# #     }


# # def retrieve_relevant_chunks(question, top_k=5):
# #     """Find the most relevant PDF chunks for a question."""

# #     if not chunks:
# #         raise ValueError("No PDF has been processed yet.")

# #     question_embedding = embedding_model.encode(
# #         [question],
# #         convert_to_numpy=True
# #     )[0]

# #     # Normalize vectors
# #     question_embedding = question_embedding / (
# #         np.linalg.norm(question_embedding) + 1e-10
# #     )

# #     normalized_embeddings = chunk_embeddings / (
# #         np.linalg.norm(
# #             chunk_embeddings,
# #             axis=1,
# #             keepdims=True
# #         ) + 1e-10
# #     )

# #     # Cosine similarity
# #     similarities = np.dot(
# #         normalized_embeddings,
# #         question_embedding
# #     )

# #     # Get highest scoring chunks
# #     top_indices = np.argsort(similarities)[-top_k:][::-1]

# #     results = []

# #     for index in top_indices:
# #         results.append({
# #             "text": chunks[index],
# #             "score": float(similarities[index])
# #         })

# #     return results


# # async def generate_answer(question, relevant_chunks):
# #     """Send retrieved PDF content to Groq and generate an answer."""

# #     api_key = os.environ.get("GROQ_API_KEY")

# #     if not api_key:
# #         raise ValueError("GROQ_API_KEY is not set.")

# #     context = "\n\n".join(
# #         item["text"] for item in relevant_chunks
# #     )

# #     prompt = f"""
# # You are AskMyNotes, an AI assistant that answers questions
# # using the user's uploaded PDF.

# # Answer the question using ONLY the information provided
# # in the context below.

# # If the answer cannot be found in the context, say:
# # "I couldn't find the answer in the uploaded PDF."

# # Context:
# # {context}

# # Question:
# # {question}

# # Answer:
# # """

# #     headers = {
# #         "Authorization": f"Bearer {api_key}",
# #         "Content-Type": "application/json"
# #     }

# #     data = {
# #         "model": "llama-3.3-70b-versatile",
# #         "messages": [
# #             {
# #                 "role": "system",
# #                 "content": "You answer questions using provided document context."
# #             },
# #             {
# #                 "role": "user",
# #                 "content": prompt
# #             }
# #         ],
# #         "temperature": 0.2
# #     }

# #     async with httpx.AsyncClient(timeout=60.0) as client:

# #         response = await client.post(
# #             "https://api.groq.com/openai/v1/chat/completions",
# #             headers=headers,
# #             json=data
# #         )

# #     if response.status_code != 200:
# #         raise Exception(
# #             f"Groq API error: {response.status_code} {response.text}"
# #         )

# #     result = response.json()

# #     answer = result["choices"][0]["message"]["content"]

# #     return answer


# # async def ask_question(question, top_k=5):
# #     """
# #     Complete RAG pipeline:

# #     Question
# #        ↓
# #     Embedding
# #        ↓
# #     Retrieve relevant chunks
# #        ↓
# #     Groq
# #        ↓
# #     Answer
# #     """

# #     relevant_chunks = retrieve_relevant_chunks(
# #         question,
# #         top_k=top_k
# #     )

# #     answer = await generate_answer(
# #         question,
# #         relevant_chunks
# #     )

# #     sources = [
# #         {
# #             "text": item["text"],
# #             "score": item["score"]
# #         }
# #         for item in relevant_chunks
# #     ]

# #     return {
# #         "answer": answer,
# #         "sources": sources
# #     }
# from dotenv import load_dotenv
# import os
# import numpy as np
# from pypdf import PdfReader
# from sentence_transformers import SentenceTransformer
# import httpx

# load_dotenv()

# # Load embedding model
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# # Store processed PDF in memory
# chunks = []
# chunk_embeddings = []


# def extract_text_from_pdf(pdf_path):
#     reader = PdfReader(pdf_path)

#     text = ""

#     for page in reader.pages:
#         page_text = page.extract_text()

#         if page_text:
#             text += page_text + "\n"

#     return text


# def create_chunks(text, chunk_size=500, overlap=100):
#     words = text.split()

#     result = []

#     start = 0

#     while start < len(words):
#         end = start + chunk_size

#         chunk = " ".join(words[start:end])

#         if chunk.strip():
#             result.append(chunk)

#         start += chunk_size - overlap

#     return result


# def create_embeddings(text_chunks):
#     return embedding_model.encode(
#         text_chunks,
#         convert_to_numpy=True
#     )


# def process_pdf(pdf_path):
#     global chunks
#     global chunk_embeddings

#     print("Processing PDF...")

#     text = extract_text_from_pdf(pdf_path)

#     if not text.strip():
#         raise ValueError("No readable text found in the PDF.")

#     print("PDF text extracted.")

#     chunks = create_chunks(text)

#     print(f"Created {len(chunks)} chunks.")

#     chunk_embeddings = create_embeddings(chunks)

#     print("Embeddings created.")

#     return {
#         "chunks": len(chunks),
#         "message": "PDF processed successfully"
#     }


# def retrieve_relevant_chunks(question, top_k=5):

#     if not chunks:
#         raise ValueError(
#             "No PDF has been processed. Upload a PDF first."
#         )

#     print("Creating question embedding...")

#     question_embedding = embedding_model.encode(
#         [question],
#         convert_to_numpy=True
#     )[0]

#     question_embedding = question_embedding / (
#         np.linalg.norm(question_embedding) + 1e-10
#     )

#     normalized_embeddings = chunk_embeddings / (
#         np.linalg.norm(
#             chunk_embeddings,
#             axis=1,
#             keepdims=True
#         ) + 1e-10
#     )

#     similarities = np.dot(
#         normalized_embeddings,
#         question_embedding
#     )

#     top_indices = np.argsort(similarities)[-top_k:][::-1]

#     results = []

#     for index in top_indices:
#         results.append({
#             "text": chunks[index],
#             "score": float(similarities[index])
#         })

#     print("Relevant chunks retrieved.")

#     return results


# async def generate_answer(question, relevant_chunks):

#     api_key = os.environ.get("GROQ_API_KEY")
#     print("GROQ KEY AVAILABLE:", bool(api_key))

#     if not api_key:
#         raise ValueError(
#             "GROQ_API_KEY is not set."
#         )

#     context = "\n\n".join(
#         item["text"]
#         for item in relevant_chunks
#     )

#     prompt = f"""
# You are AskMyNotes.

# Answer the user's question using ONLY the information
# provided in the PDF context.

# If the answer is not present in the PDF, say:
# "I couldn't find the answer in the uploaded PDF."

# PDF CONTEXT:
# {context}

# QUESTION:
# {question}

# ANSWER:
# """

#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": (
#                     "You answer questions using the "
#                     "provided PDF context."
#                 )
#             },
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ],
#         "temperature": 0.2
#     }

#     print("Sending request to Groq...")

#     async with httpx.AsyncClient(timeout=60.0) as client:

#         response = await client.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers=headers,
#             json=data
#         )

#     print("Groq status:", response.status_code)

#     if response.status_code != 200:
#         print("Groq response:", response.text)

#         raise Exception(
#             f"Groq API error: {response.status_code}"
#         )

#     result = response.json()

#     answer = result["choices"][0]["message"]["content"]

#     print("Answer generated successfully.")

#     return answer


# async def ask_question(question, top_k=5):

#     print(f"Question received: {question}")

#     relevant_chunks = retrieve_relevant_chunks(
#         question,
#         top_k
#     )

#     answer = await generate_answer(
#         question,
#         relevant_chunks
#     )

#     sources = [
#         {
#             "text": item["text"],
#             "score": item["score"]
#         }
#         for item in relevant_chunks
#     ]

#     return {
#         "answer": answer,
#         "sources": sources
#     }

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

    # Add your Render frontend URL later
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

        # Import only when needed
        from rag import process_pdf

        result = process_pdf(file_path)

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

        # Import only when needed
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