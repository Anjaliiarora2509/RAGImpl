import os
from groq import Groq
from dotenv import load_dotenv

import config
from ingestion import ingest_docs, Chunk
from vector_store import HuggingFaceEmbedder, ChromaVectorStore
from retrieval import SimilarityRetriever

load_dotenv()


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file.")
    return Groq(api_key=api_key)


def build_context(chunks: list[Chunk]) -> str:
    return "\n\n".join(f"[{c.source}]\n{c.text}" for c in chunks)


def chat(query: str, retriever: SimilarityRetriever, k: int = 5) -> str:
    chunks = retriever.retrieve(query, k=k)
    context = build_context(chunks)
    messages = [
        {"role": "system", "content": f"Answer using only the context below.\n\n{context}"},
        {"role": "user", "content": query},
    ]
    client = get_groq_client()
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    # --- Ingest & store (runs once; upsert makes reruns safe) ---
    chunks = ingest_docs()
    print(f"Loaded {len(chunks)} chunks")

    embedder = HuggingFaceEmbedder()
    store = ChromaVectorStore()
    store.add(chunks)
    print("Chunks stored in vector store.")

    # --- Retrieval + LLM ---
    retriever = SimilarityRetriever(embedder, store)
    query = "What is this document about?"
    print(f"\nQuery: {query}")
    answer = chat(query, retriever)
    print(f"Answer: {answer}")