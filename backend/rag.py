from dotenv import load_dotenv
import os
import numpy as np
from pypdf import PdfReader
import httpx


# ==========================================
# Environment
# ==========================================

load_dotenv()


# ==========================================
# Embedding model
# ==========================================

embedding_model = None


def get_embedding_model():
    """
    Load the SentenceTransformer model only when
    it is actually needed.

    This prevents the model from loading when
    FastAPI starts.
    """

    global embedding_model

    if embedding_model is None:

        print("Loading embedding model...")

        from sentence_transformers import SentenceTransformer

        embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

    return embedding_model


# ==========================================
# Store processed PDF in memory
# ==========================================

chunks = []
chunk_embeddings = []


# ==========================================
# Extract PDF text
# ==========================================

def extract_text_from_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ==========================================
# Create chunks
# ==========================================

def create_chunks(
    text,
    chunk_size=500,
    overlap=100
):

    words = text.split()

    result = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():
            result.append(chunk)

        start += chunk_size - overlap

    return result


# ==========================================
# Create embeddings
# ==========================================

def create_embeddings(text_chunks):

    model = get_embedding_model()

    return model.encode(
        text_chunks,
        convert_to_numpy=True
    )


# ==========================================
# Process PDF
# ==========================================

def process_pdf(pdf_path):

    global chunks
    global chunk_embeddings

    print("Processing PDF...")

    text = extract_text_from_pdf(
        pdf_path
    )

    if not text.strip():

        raise ValueError(
            "No readable text found in the PDF."
        )

    print("PDF text extracted.")

    chunks = create_chunks(text)

    print(
        f"Created {len(chunks)} chunks."
    )

    chunk_embeddings = create_embeddings(
        chunks
    )

    print("Embeddings created.")

    return {
        "chunks": len(chunks),
        "message": "PDF processed successfully"
    }


# ==========================================
# Retrieve relevant chunks
# ==========================================

def retrieve_relevant_chunks(
    question,
    top_k=5
):

    if not chunks:

        raise ValueError(
            "No PDF has been processed. "
            "Upload a PDF first."
        )

    print(
        "Creating question embedding..."
    )

    model = get_embedding_model()

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )[0]

    # Normalize question vector
    question_embedding = (
        question_embedding /
        (
            np.linalg.norm(
                question_embedding
            ) + 1e-10
        )
    )

    # Normalize chunk vectors
    normalized_embeddings = (
        chunk_embeddings /
        (
            np.linalg.norm(
                chunk_embeddings,
                axis=1,
                keepdims=True
            ) + 1e-10
        )
    )

    # Cosine similarity
    similarities = np.dot(
        normalized_embeddings,
        question_embedding
    )

    # Get top chunks
    top_indices = np.argsort(
        similarities
    )[-top_k:][::-1]

    results = []

    for index in top_indices:

        results.append(
            {
                "text": chunks[index],
                "score": float(
                    similarities[index]
                )
            }
        )

    print(
        "Relevant chunks retrieved."
    )

    return results


# ==========================================
# Generate answer using Groq
# ==========================================

async def generate_answer(
    question,
    relevant_chunks
):

    api_key = os.environ.get(
        "GROQ_API_KEY"
    )

    print(
        "GROQ KEY AVAILABLE:",
        bool(api_key)
    )

    if not api_key:

        raise ValueError(
            "GROQ_API_KEY is not set."
        )

    context = "\n\n".join(
        item["text"]
        for item in relevant_chunks
    )

    prompt = f"""
You are AskMyNotes.

Answer the user's question using ONLY
the information provided in the PDF context.

If the answer is not present in the PDF,
say:

"I couldn't find the answer in the uploaded PDF."

PDF CONTEXT:

{context}

QUESTION:

{question}

ANSWER:
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",

        "messages": [
            {
                "role": "system",
                "content": (
                    "You answer questions using "
                    "the provided PDF context."
                )
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        "temperature": 0.2
    }

    print(
        "Sending request to Groq..."
    )

    async with httpx.AsyncClient(
        timeout=60.0
    ) as client:

        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )

    print(
        "Groq status:",
        response.status_code
    )

    if response.status_code != 200:

        print(
            "Groq response:",
            response.text
        )

        raise Exception(
            f"Groq API error: "
            f"{response.status_code}"
        )

    result = response.json()

    answer = result[
        "choices"
    ][0][
        "message"
    ][
        "content"
    ]

    print(
        "Answer generated successfully."
    )

    return answer


# ==========================================
# Ask Question
# ==========================================

async def ask_question(
    question,
    top_k=5
):

    print(
        f"Question received: {question}"
    )

    relevant_chunks = (
        retrieve_relevant_chunks(
            question,
            top_k
        )
    )

    answer = await generate_answer(
        question,
        relevant_chunks
    )

    sources = [
        {
            "text": item["text"],
            "score": item["score"]
        }

        for item in relevant_chunks
    ]

    return {
        "answer": answer,
        "sources": sources
    }