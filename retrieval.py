from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ingestion import Chunk
from vector_store import BaseEmbedder, BaseVectorStore


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> List[Chunk]:
        ...


class SimilarityRetriever(BaseRetriever):
    def __init__(self, embedder: BaseEmbedder, store: BaseVectorStore):
        self._embedder = embedder
        self._store = store

    def retrieve(self, query: str, k: int = 5) -> List[Chunk]:
        query_vec = self._embedder.embed([query])[0]
        return self._store.search(query_vec, k)
