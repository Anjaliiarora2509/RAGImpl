from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import chromadb

from ingestion import Chunk


class BaseEmbedder(ABC):
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        ...


class HuggingFaceEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, show_progress_bar=False).tolist()


class BaseVectorStore(ABC):
    @abstractmethod
    def add(self, chunks: List[Chunk]) -> None:
        ...

    @abstractmethod
    def search(self, query_vec: List[float], k: int) -> List[Chunk]:
        ...


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, persist_dir: str = ".chroma"):
        client = chromadb.PersistentClient(path=persist_dir)
        self._collection = client.get_or_create_collection("rag_chunks")

    def add(self, chunks: List[Chunk]) -> None:
        if not chunks:
            return
        self._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=[{"source": c.source} for c in chunks],
        )

    def search(self, query_vec: List[float], k: int) -> List[Chunk]:
        results = self._collection.query(
            query_embeddings=[query_vec],
            n_results=k,
            include=["documents", "metadatas"],
        )
        chunks: List[Chunk] = []
        for chunk_id, text, meta in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
        ):
            chunks.append(Chunk(text=text, source=meta["source"], chunk_id=chunk_id))
        return chunks
