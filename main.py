import os
from groq import Groq
from dotenv import load_dotenv

from ingestion import ingest_docs
from vector_store import HuggingFaceEmbedder, ChromaVectorStore

load_dotenv()


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file.")
    return Groq(api_key=api_key)


def chat(messages: list[dict], model: str = "llama-3.3-70b-versatile") -> str:
    client = get_groq_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    chunks = ingest_docs()
    print(f"Loaded {len(chunks)} chunks")

    embedder = HuggingFaceEmbedder()
    store = ChromaVectorStore()

    store.add(chunks)

    print("Chunks embedded and stored in vector store.")