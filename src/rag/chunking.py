"""Split documents into overlapping chunks of words.

Chunks keep a reference to the file they came from, so every answer can cite its source.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str  # file name, e.g. "angular-signals.md"
    index: int  # position of the chunk inside its file


def chunk_text(text: str, source: str, size: int = 80, overlap: int = 20) -> list[Chunk]:
    """Split `text` into chunks of about `size` words, sharing `overlap` words with the previous chunk.

    The overlap keeps sentences that fall on a chunk border retrievable from both sides.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must be >= 0 and smaller than size")

    words = text.split()
    if not words:
        return []

    step = size - overlap
    chunks: list[Chunk] = []
    for index, start in enumerate(range(0, len(words), step)):
        window = words[start : start + size]
        chunks.append(Chunk(text=" ".join(window), source=source, index=index))
        if start + size >= len(words):
            break
    return chunks


def load_documents(docs_dir: str | Path) -> dict[str, str]:
    """Read every .md and .txt file in a folder. Returns {file name: text}."""
    folder = Path(docs_dir)
    if not folder.is_dir():
        raise FileNotFoundError(f"Documents folder not found: {folder}")

    documents: dict[str, str] = {}
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() in {".md", ".txt"}:
            documents[path.name] = path.read_text(encoding="utf-8")
    if not documents:
        raise ValueError(f"No .md or .txt files found in {folder}")
    return documents


def chunk_documents(documents: dict[str, str], size: int = 80, overlap: int = 20) -> list[Chunk]:
    chunks: list[Chunk] = []
    for source, text in documents.items():
        chunks.extend(chunk_text(text, source, size=size, overlap=overlap))
    return chunks
