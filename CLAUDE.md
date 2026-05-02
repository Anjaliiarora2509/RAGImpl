# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pip install -r requirements.txt
```

Requires a `.env` file at the project root with:
```
GROQ_API_KEY=<your_key>
```

## Running

```bash
python main.py
```

## Architecture

This is an early-stage RAG (Retrieval-Augmented Generation) pipeline. The intended data flow is:

```
docs/ → ingestion.py → vector_store.py → retrieval.py → main.py (LLM chat)
```

**Current state:** Only the LLM layer is implemented. The three pipeline modules (`ingestion.py`, `vector_store.py`, `retrieval.py`) are empty stubs.

### Key files

- [main.py](main.py) — Entry point. Initializes a Groq client and exposes a `chat(messages, model)` function. When the RAG pipeline is wired up, retrieval context should be injected here before calling the LLM.
- [config.py](config.py) — Defines `LLM_MODEL` and `PLAN_LLM_MODEL`. **Use these constants** rather than hardcoding model strings elsewhere (note: `main.py` currently hardcodes `"llama-3.3-70b-versatile"` — this should be aligned with `config.py`).
- [ingestion.py](ingestion.py) — Intended for document loading and chunking.
- [vector_store.py](vector_store.py) — Intended for embedding storage and management.
- [retrieval.py](retrieval.py) — Intended for similarity search against the vector store.

## Code Design Principles

Follow SOLID principles on all new code and refactors:

- **S** — Each class has one reason to change. Extraction agents,
  search agents, and output formatters are separate classes.
- **O** — Add new retrieval strategies by subclassing, not by
  adding if/else branches to existing classes.
- **L** — Subclasses of BaseTool must be drop-in replacements
  (same method signatures, no narrowed inputs).
- **D** — Agent classes depend on abstractions (BaseTool, BaseRetriever),
  never on concrete implementations directly.

When refactoring, flag any violation found and propose the fix
before implementing.

## Dependencies

- `groq` — LLM inference via Groq API (LLaMA models)
- `python-dotenv` — loads `.env` at runtime
- `uvicorn[standard]` — included for a planned FastAPI HTTP layer, not yet implemented
