# ingestion.py — Module Overview

## What is it?

`ingestion.py` is the first step in the RAG (Retrieval-Augmented Generation) pipeline.
Its job is to take raw documents (like PDFs or text files) from the `docs/` folder,
read their contents, and break them into smaller, manageable pieces called **chunks**.
These chunks are then passed to the next stage of the pipeline for storage and search.

---

## Why was it added?

A language model (LLM) can only read a limited amount of text at a time. If you have a
large document — say, a 50-page PDF — you cannot feed the whole thing to the model at once.

`ingestion.py` solves this by:
- Reading the full document
- Splitting it into smaller chunks that fit within the model's limit
- Keeping some overlap between chunks so no information is lost at the boundaries

---

## How it fits into the overall workflow

```
docs/ (PDF, TXT, MD files)
        │
        ▼
  ingestion.py        ← YOU ARE HERE
  (load + chunk)
        │
        ▼
  vector_store.py     (store chunks as searchable vectors)
        │
        ▼
  retrieval.py        (find the most relevant chunks for a query)
        │
        ▼
  main.py             (send relevant chunks + query to the LLM)
```

`ingestion.py` feeds everything downstream. Without it, there is nothing to search or retrieve.

---

## Key Components

### `Chunk`
A simple container that holds one piece of text extracted from a document. Each chunk has:
- **text** — the actual content
- **source** — which file it came from
- **chunk_id** — a unique label (e.g. `report.pdf::3` means the 4th chunk from `report.pdf`)

### `DocumentLoader`
Knows how to read a file and return its full text. Different file types are handled by
dedicated subclasses:
- **PDFLoader** — reads `.pdf` files
- **PlainTextLoader** — reads `.txt` and `.md` files

Adding support for a new file type (e.g. Word documents) only requires adding a new subclass —
nothing else needs to change.

### `TextChunker`
Takes the full text from a document and slices it into overlapping chunks.
- **Chunk size** — how many characters each chunk contains (default: 500, set in `config.py`)
- **Overlap** — how many characters are shared between consecutive chunks (default: 100)

The overlap ensures that a sentence split across a boundary is still fully captured in at
least one chunk.

### `ingest_docs()`
The main function that ties everything together. Call this to process all documents in
the `docs/` folder in one step.

---

## Data Flow

```
docs/ folder
    │
    ├── scan for supported files (.pdf, .txt, .md)
    │
    ├── for each file → DocumentLoader reads raw text
    │
    ├── TextChunker splits text into overlapping chunks
    │
    └── returns List[Chunk]  →  passed to vector_store.py
```

---

## Example Scenario

Imagine you have a PDF ticket (`EmiratesTicket.pdf`) in the `docs/` folder.

1. `ingest_docs()` scans the folder and finds the PDF.
2. `PDFLoader` opens it and extracts all the text from every page into one long string.
3. `TextChunker` slices that string into chunks of 500 characters each, with 100 characters
   of overlap between consecutive chunks.
4. The result is a list of `Chunk` objects like:

   | chunk_id | source | text (preview) |
   |---|---|---|
   | `EmiratesTicket.pdf::0` | EmiratesTicket.pdf | `Passenger: John Doe Flight: EK202...` |
   | `EmiratesTicket.pdf::1` | EmiratesTicket.pdf | `...EK202 Departure: Dubai 14:30 Arr...` |
   | `EmiratesTicket.pdf::2` | EmiratesTicket.pdf | `...Arrival: London 18:45 Seat: 12A...` |

   Notice how chunks 0 and 1 share some text — that is the overlap at work.

5. This list is handed off to `vector_store.py` for the next stage.

---

## Configuration

| Setting | File | Default | Purpose |
|---|---|---|---|
| `CHUNK_SIZE` | `config.py` | 500 | Max characters per chunk |
| `CHUNK_OVERLAP` | `config.py` | 100 | Characters shared between chunks |

To tune chunking behaviour, edit these values in `config.py` — no changes needed in `ingestion.py`.
