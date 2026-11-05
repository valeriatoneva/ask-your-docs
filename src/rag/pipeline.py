"""Glue code: documents -> chunks -> vectors -> retrieval -> answer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chunking import Chunk, chunk_documents, load_documents
from .embeddings import Embedder, get_embedder
from .generator import Generator, get_generator
from .store import VectorStore


@dataclass
class Answer:
    question: str
    text: str
    hits: list[tuple[Chunk, float]]

    @property
    def sources(self) -> list[str]:
        seen: list[str] = []
        for chunk, _ in self.hits:
            if chunk.source not in seen:
                seen.append(chunk.source)
        return seen


class RagPipeline:
    def __init__(self, embedder: Embedder, store: VectorStore, generator: Generator) -> None:
        self.embedder = embedder
        self.store = store
        self.generator = generator

    @classmethod
    def build(
        cls,
        docs_dir: str | Path,
        backend: str = "tfidf",
        generator: str = "extractive",
        size: int = 80,
        overlap: int = 20,
    ) -> "RagPipeline":
        chunks = chunk_documents(load_documents(docs_dir), size=size, overlap=overlap)
        embedder = get_embedder(backend)
        texts = [c.text for c in chunks]
        embedder.fit(texts)
        store = VectorStore(chunks, embedder.embed_documents(texts))
        return cls(embedder, store, get_generator(generator))

    @classmethod
    def load(cls, index_dir: str | Path, generator: str = "extractive") -> "RagPipeline":
        chunks, backend = VectorStore.load_chunks(index_dir)
        embedder = get_embedder(backend)
        texts = [c.text for c in chunks]
        embedder.fit(texts)
        # TF-IDF vectors depend on the fitted vocabulary, so they are recomputed (cheap).
        # API embeddings are expensive, so they are read from disk.
        vectors = embedder.embed_documents(texts) if backend == "tfidf" else VectorStore.load_vectors(index_dir)
        return cls(embedder, VectorStore(chunks, vectors), get_generator(generator))

    def save(self, index_dir: str | Path) -> None:
        self.store.save(index_dir, self.embedder.name)

    def retrieve(self, question: str, k: int = 3) -> list[tuple[Chunk, float]]:
        return self.store.search(self.embedder.embed_query(question), k=k)

    def ask(self, question: str, k: int = 3) -> Answer:
        hits = self.retrieve(question, k=k)
        return Answer(question=question, text=self.generator.generate(question, hits), hits=hits)
