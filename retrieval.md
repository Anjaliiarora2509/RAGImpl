# retrieval.py — Module Overview

## What is it?

`retrieval.py` is the third step in the RAG pipeline. It takes a user's question,
converts it into a vector, and searches the vector store for the chunks that are
most semantically similar to that question. Those chunks are then passed to the LLM
as context.

---

## Why was it added?

The vector store holds all document chunks as vectors. But to find the *right* chunks
for a given question, you need to convert the question into a vector too — then compare
it against every stored vector and return the closest matches.

`retrieval.py` is the bridge between the stored knowledge and the LLM. Without it,
the model has no document context to answer from.

---

## How it fits into the overall workflow

```
vector_store.py   (persisted chunks + vectors)
      │
      ▼
retrieval.py            ← YOU ARE HERE
(embed query → search)
      │
      ▼
main.py           (build context → call LLM)
```

---

## Key Components

### `BaseRetriever`
An abstract blueprint with one method: `retrieve(query, k) -> List[Chunk]`.

`main.py` depends on this abstraction — meaning you can swap in a different retrieval
strategy (e.g. MMR, hybrid search) by creating a new subclass, with no changes needed
in `main.py`.

### `SimilarityRetriever`
The concrete implementation. It takes two dependencies at construction time:

- `embedder` — a `BaseEmbedder` to convert the query into a vector
- `store` — a `BaseVectorStore` to search against

**`retrieve(query, k=5)`** does two things:
1. Embeds the query string into a vector using the embedder
2. Calls `store.search(query_vec, k)` to return the `k` most similar chunks

Both dependencies are abstractions — `SimilarityRetriever` never imports
`HuggingFaceEmbedder` or `ChromaVectorStore` directly.

---

## Data Flow

```
User query (str)
      │
      ▼
BaseEmbedder.embed([query])     converts question → vector
      │
      ▼
BaseVectorStore.search(query_vec, k)    finds top-k nearest chunks
      │
      ▼
List[Chunk]   (most relevant context)  →  main.py
```

---

## Example Scenario

The document store contains chunks from a flight ticket PDF. The user asks:

> *"What seat is the passenger in?"*

1. `SimilarityRetriever.retrieve("What seat is the passenger in?", k=3)` is called.
2. The question is embedded into a vector.
3. ChromaDB returns the 3 chunks whose vectors are closest to the question vector.
4. The chunk containing `Seat: 12A` ranks highest and is returned.
5. `main.py` passes it as context to the LLM, which answers: *"The passenger is in seat 12A."*

---

## How to call it

```python
from vector_store import HuggingFaceEmbedder, ChromaVectorStore
from retrieval import SimilarityRetriever

embedder = HuggingFaceEmbedder()
store = ChromaVectorStore()           # connects to existing .chroma/ on disk
retriever = SimilarityRetriever(embedder, store)

chunks = retriever.retrieve("What seat is the passenger in?", k=3)
for c in chunks:
    print(c.chunk_id, c.text)
```

The `.chroma/` store must be populated first by running the ingestion + `store.add(chunks)` step.

---

## Extending with a new retrieval strategy

Because `main.py` depends on `BaseRetriever`, adding a new strategy requires no
changes to existing code — just subclass:

```python
class MMRRetriever(BaseRetriever):
    def retrieve(self, query: str, k: int = 5) -> List[Chunk]:
        # Maximal Marginal Relevance logic here
        ...
```

Pass it into `main.py` in place of `SimilarityRetriever` and everything works.
