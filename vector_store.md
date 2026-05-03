# vector_store.py — Module Overview

## What is it?

`vector_store.py` is the second step in the RAG pipeline. It takes the text chunks
produced by `ingestion.py`, converts them into **vectors** (lists of numbers that
represent meaning), and stores them in a database that can be searched later.

---

## Why was it added?

Plain text cannot be searched by meaning — only by exact keywords. Vectors fix this.
Two sentences that mean the same thing will produce similar vectors, even if they use
different words. This allows the pipeline to find the most *relevant* chunks for any
user query, not just chunks that contain matching words.

---

## How it fits into the overall workflow

```
ingestion.py   (List[Chunk])
      │
      ▼
vector_store.py         ← YOU ARE HERE
(embed + store)
      │
      ▼
retrieval.py   (search by query)
      │
      ▼
main.py        (send context + query to LLM)
```

---

## Key Components

### `BaseEmbedder`
An abstract blueprint that defines one method: `embed(texts) → vectors`.
Any embedder in the project must follow this contract. This keeps the rest of
the code independent from the specific embedding tool being used.

### `HuggingFaceEmbedder`
The concrete embedder. Uses a lightweight model (`all-MiniLM-L6-v2`) from the
`sentence-transformers` library that runs **locally** — no API key or internet
connection required at inference time.

- Input: a list of strings
- Output: a list of 384-dimensional float vectors (one per string)
- The model loads once and is reused for every call

### `BaseVectorStore`
An abstract blueprint that defines two methods:
- `add(chunks)` — save chunks into the store
- `search(query_vec, k)` — find the `k` most similar chunks for a given query vector

### `ChromaVectorStore`
The concrete store backed by **ChromaDB**, a lightweight vector database that
persists data to disk inside a `.chroma/` folder.

- **`add(chunks)`** — saves each chunk using `upsert`, so re-running the pipeline
  never creates duplicate entries
- **`search(query_vec, k)`** — queries ChromaDB for the nearest vectors and returns
  matching chunks as `Chunk` objects ready for the retrieval stage

---

## Data Flow

```
List[Chunk]  (text + source + chunk_id)
      │
      ▼
HuggingFaceEmbedder.embed()     converts text → float vectors
      │
      ▼
ChromaVectorStore.add()         stores (chunk + vector) to disk
      │
      ▼
  .chroma/ folder               persisted vector database

      ▼  (at query time)

ChromaVectorStore.search(query_vec, k)
      │
      ▼
  List[Chunk]  (top-k most relevant)  →  retrieval.py
```

---

## Example Scenario

Suppose two chunks were ingested from a PDF:

| chunk_id | text |
|---|---|
| `ticket.pdf::0` | `Passenger: John Doe Flight: EK202 Departure: Dubai` |
| `ticket.pdf::1` | `Arrival: London 18:45 Seat: 12A Baggage: 30kg` |

1. `HuggingFaceEmbedder.embed()` converts both texts into vectors.
2. `ChromaVectorStore.add()` saves both chunks with their vectors to `.chroma/`.
3. Later, when a user asks *"What seat is John on?"*, that question is also
   embedded into a vector and `search(query_vec, k=2)` returns `ticket.pdf::1`
   as the closest match because its meaning is most similar.

---

## Configuration

| Setting | Where | Default | Purpose |
|---|---|---|---|
| Embedding model | `HuggingFaceEmbedder.__init__` | `all-MiniLM-L6-v2` | Model used to generate vectors |
| Persist directory | `ChromaVectorStore.__init__` | `.chroma/` | Where ChromaDB saves data on disk |

---

## Dependencies

| Package | Purpose |
|---|---|
| `sentence-transformers` | Loads and runs the local embedding model |
| `chromadb` | Vector database for storing and searching embeddings |

Install with:
```
pip install sentence-transformers chromadb
```
