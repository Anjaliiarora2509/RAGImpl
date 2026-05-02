from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List

import config


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: str


class DocumentLoader(ABC):
    """Loads raw text from a single file."""

    @abstractmethod
    def load(self, path: Path) -> str:
        ...

    @classmethod
    def for_path(cls, path: Path) -> "DocumentLoader":
        """Return the right loader for the file extension."""
        ext = path.suffix.lower()
        if ext == ".pdf":
            return PDFLoader()
        if ext in (".md", ".txt"):
            return PlainTextLoader()
        raise ValueError(f"No loader registered for extension '{ext}'")


class PDFLoader(DocumentLoader):
    def load(self, path: Path) -> str:
        try:
            import pypdf
        except ImportError as exc:
            raise ImportError("pypdf is required for PDF loading: pip install pypdf") from exc

        reader = pypdf.PdfReader(str(path))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)


class PlainTextLoader(DocumentLoader):
    def load(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")


class TextChunker:
    """Splits raw text into overlapping Chunk objects."""

    def __init__(self, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, source: str) -> List[Chunk]:
        chunks: List[Chunk] = []
        start = 0
        idx = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(
                    text=chunk_text,
                    source=source,
                    chunk_id=f"{source}::{idx}",
                ))
                idx += 1
            start += self.chunk_size - self.overlap
        return chunks


def ingest_docs(docs_dir: str = "docs") -> List[Chunk]:
    """Load and chunk every supported file under docs_dir."""
    root = Path(docs_dir)
    all_chunks: List[Chunk] = []
    chunker = TextChunker()

    for path in root.iterdir():
        if not path.is_file():
            continue
        try:
            loader = DocumentLoader.for_path(path)
        except ValueError:
            continue
        text = loader.load(path)
        all_chunks.extend(chunker.chunk(text, source=path.name))

    return all_chunks
