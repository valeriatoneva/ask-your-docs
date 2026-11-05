"""A tiny in-memory vector store with save/load.

With normalised vectors, cosine similarity is a matrix-vector dot product, so a
plain NumPy array is enough for a few thousand chunks. No database needed.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .chunking import Chunk


class VectorStore:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        self.chunks = chunks
        self.vectors = vectors

    def search(self, query_vector: np.ndarray, k: int = 3) -> list[tuple[Chunk, float]]:
        """Return the k most similar chunks with their cosine similarity score."""
        if not self.chunks:
            return []
        scores = self.vectors @ query_vector
        k = min(k, len(self.chunks))
        top = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top]

    def save(self, folder: str | Path, backend: str) -> None:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        (path / "chunks.json").write_text(
            json.dumps([asdict(c) for c in self.chunks], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (path / "meta.json").write_text(json.dumps({"backend": backend}), encoding="utf-8")
        np.save(path / "vectors.npy", self.vectors)

    @staticmethod
    def load_chunks(folder: str | Path) -> tuple[list[Chunk], str]:
        path = Path(folder)
        if not (path / "chunks.json").exists():
            raise FileNotFoundError(f"No index found in {path}. Run the 'index' command first.")
        chunks = [Chunk(**item) for item in json.loads((path / "chunks.json").read_text(encoding="utf-8"))]
        backend = json.loads((path / "meta.json").read_text(encoding="utf-8"))["backend"]
        return chunks, backend

    @staticmethod
    def load_vectors(folder: str | Path) -> np.ndarray:
        return np.load(Path(folder) / "vectors.npy")
