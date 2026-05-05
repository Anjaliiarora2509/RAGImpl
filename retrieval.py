from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict

from rank_bm25 import BM25Okapi

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


class HybridRetriever(BaseRetriever):
    """Combines dense vector search and BM25 via Reciprocal Rank Fusion."""

    def __init__(self, embedder: BaseEmbedder, store: BaseVectorStore, chunks: List[Chunk], rrf_k: int = 60):
        self._embedder = embedder
        self._store = store
        self._chunks = chunks
        self._rrf_k = rrf_k

        tokenized = [c.text.lower().split() for c in chunks]
        self._bm25 = BM25Okapi(tokenized)

    def _rrf_score(self, rank: int) -> float:
        return 1.0 / (self._rrf_k + rank + 1)

    def retrieve(self, query: str, k: int = 5) -> List[Chunk]:
        # Dense retrieval — fetch more candidates than k for better fusion
        fetch = min(k * 2, len(self._chunks))
        query_vec = self._embedder.embed([query])[0]
        dense_chunks = self._store.search(query_vec, fetch)

        # BM25 retrieval over all chunks
        tokenized_query = query.lower().split()
        bm25_scores = self._bm25.get_scores(tokenized_query)
        bm25_ranked_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:fetch]

        # RRF fusion — accumulate scores by chunk_id
        rrf: Dict[str, float] = {}

        for rank, chunk in enumerate(dense_chunks):
            rrf[chunk.chunk_id] = rrf.get(chunk.chunk_id, 0.0) + self._rrf_score(rank)

        for rank, idx in enumerate(bm25_ranked_indices):
            cid = self._chunks[idx].chunk_id
            rrf[cid] = rrf.get(cid, 0.0) + self._rrf_score(rank)

        # Sort by combined RRF score and return top-k chunks
        top_ids = sorted(rrf, key=lambda cid: rrf[cid], reverse=True)[:k]
        id_to_chunk = {c.chunk_id: c for c in self._chunks}
        return [id_to_chunk[cid] for cid in top_ids if cid in id_to_chunk]
