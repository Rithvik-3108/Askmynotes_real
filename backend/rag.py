from dotenv import load_dotenv
import os
import numpy as np
from pypdf import PdfReader
import httpx

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# Environment
# ==========================================

load_dotenv()


# ==========================================
# Store processed PDF
# ==========================================

chunks = []

vectorizer = None
chunk_vectors = None


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
# Create TF-IDF vectors
# ==========================================

def create_embeddings(text_chunks):

    global vectorizer

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(
        text_chunks
    )

    return vectors


# ==========================================
# Process PDF
# ==========================================

def process_pdf(pdf_path):

    global chunks
    global chunk_vectors

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

    chunk_vectors = create_embeddings(
        chunks
    )

    print("TF-IDF vectors created.")

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

    if vectorizer is None or chunk_vectors is None:

        raise ValueError(
            "PDF vectors are not available."
        )

    print(
        "Creating question vector..."
    )

    question_vector = vectorizer.transform(
        [question]
    )

    similarities = cosine_similarity(
        question_vector,
        chunk_vectors
    )[0]

    top_k = min(
        top_k,
        len(chunks)
    )

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