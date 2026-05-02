# RAG Pipeline Architecture

## Data Flow

```
docs/
  └── (PDF, TXT, MD files)
        │
        ▼
┌─────────────────────────────┐
│      ingestion.py           │
│  DocumentLoader             │  ← loads raw files from docs/
│  TextChunker                │  ← splits into overlapping chunks
└──────────────┬──────────────┘
               │  List[Chunk]
               ▼
┌─────────────────────────────┐
│      vector_store.py        │
│  BaseEmbedder (abstract)    │  ← converts chunks → embeddings
│  ChromaVectorStore          │  ← stores & persists vectors
└──────────────┬──────────────┘
               │  VectorStore (persisted)
               ▼
┌─────────────────────────────┐
│      retrieval.py           │
│  BaseRetriever (abstract)   │
│  SimilarityRetriever        │  ← top-k similarity search
└──────────────┬──────────────┘
               │  List[Chunk]  (relevant context)
               ▼
┌─────────────────────────────┐
│         main.py             │
│  ContextBuilder             │  ← formats chunks into prompt
│  chat(query, context)       │  ← calls Groq LLM
└──────────────┬──────────────┘
               │  str (answer)
               ▼
            User
```

## Module Breakdown

### `ingestion.py`

| Class | Responsibility (S) |
|---|---|
| `DocumentLoader` | Reads files from `docs/`, returns raw text per file |
| `TextChunker` | Splits raw text into overlapping `Chunk` objects |

- `DocumentLoader` is subclassable per file type (O) — e.g. `PDFLoader(DocumentLoader)`, `MarkdownLoader(DocumentLoader)` — no if/else branching inside the base.
- `Chunk` is a plain dataclass: `text`, `source`, `chunk_id`.

### `vector_store.py`

| Class | Responsibility (S) |
|---|---|
| `BaseEmbedder` | Abstract: `embed(texts) → List[List[float]]` |
| `HuggingFaceEmbedder` | Concrete implementation using a local embedding model |
| `BaseVectorStore` | Abstract: `add(chunks)`, `search(query_vec, k) → List[Chunk]` |
| `ChromaVectorStore` | Concrete: wraps ChromaDB for persistence |

- Agent classes depend on `BaseEmbedder` / `BaseVectorStore` abstractions, never on `ChromaVectorStore` directly (D).

### `retrieval.py`

| Class | Responsibility (S) |
|---|---|
| `BaseRetriever` | Abstract: `retrieve(query: str, k: int) → List[Chunk]` |
| `SimilarityRetriever` | Embeds query → calls `VectorStore.search` → returns top-k chunks |

- New strategies (e.g. `MMRRetriever`, `HybridRetriever`) subclass `BaseRetriever` (O), never add branches to the existing class.
- `SimilarityRetriever.__init__(self, embedder: BaseEmbedder, store: BaseVectorStore)` — depends on abstractions (D).

### `main.py`

| Class / function | Responsibility (S) |
|---|---|
| `ContextBuilder` | Formats `List[Chunk]` into a prompt string |
| `chat(query, retriever, model)` | Orchestrates: retrieve → build context → call LLM |

- `get_groq_client()` stays as-is; `chat` gains a `retriever: BaseRetriever` parameter.
- Model string sourced from `config.LLM_MODEL` (fixes current hardcoding).

## SOLID Checklist

| Principle | How it is satisfied |
|---|---|
| **S** | `DocumentLoader`, `TextChunker`, `ContextBuilder`, `SimilarityRetriever` each have one reason to change |
| **O** | New file types → new `DocumentLoader` subclass; new retrieval → new `BaseRetriever` subclass |
| **L** | All `BaseRetriever` subclasses expose the same `retrieve(query, k)` signature |
| **D** | `SimilarityRetriever` and `chat()` depend on `BaseEmbedder`/`BaseRetriever`, not concretions |

## Dependency Graph

```
main.py
  └── retrieval.py (BaseRetriever)
        └── vector_store.py (BaseEmbedder, BaseVectorStore)
              └── ingestion.py (Chunk)
config.py ←── main.py, retrieval.py (model constants)
```
