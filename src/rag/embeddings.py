"""Turn text into vectors.

Two backends share one small interface:

* ``tfidf``  - works offline, needs no API key (good for tests and a first run).
* ``gemini`` - real semantic embeddings from the Gemini API (needs GEMINI_API_KEY).

Both return L2-normalised vectors, so cosine similarity is just a dot product.
"""

from __future__ import annotations

import os
from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Embedder(Protocol):
    name: str

    def fit(self, texts: list[str]) -> None: ...
    def embed_documents(self, texts: list[str]) -> np.ndarray: ...
    def embed_query(self, text: str) -> np.ndarray: ...


def _normalise(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class TfidfEmbedder:
    """Keyword-style vectors. Fast and offline, but does not understand synonyms."""

    name = "tfidf"

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))

    def fit(self, texts: list[str]) -> None:
        self._vectorizer.fit(texts)

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return _normalise(self._vectorizer.transform(texts).toarray())

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_documents([text])[0]


class GeminiEmbedder:
    """Semantic vectors from the Gemini embeddings API."""

    name = "gemini"
    _BATCH_SIZE = 50

    def __init__(self, model: str | None = None) -> None:
        from google import genai  # imported here so the offline backend needs no extra package

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
        self._client = genai.Client(api_key=api_key)
        self._model = model or os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

    def fit(self, texts: list[str]) -> None:
        return None  # nothing to learn: the model is pre-trained

    def _embed(self, texts: list[str], task_type: str) -> np.ndarray:
        from google.genai import types

        vectors: list[list[float]] = []
        for start in range(0, len(texts), self._BATCH_SIZE):
            batch = texts[start : start + self._BATCH_SIZE]
            response = self._client.models.embed_content(
                model=self._model,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            vectors.extend(item.values for item in response.embeddings)
        return _normalise(np.array(vectors, dtype=np.float32))

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        return self._embed(texts, "RETRIEVAL_DOCUMENT")

    def embed_query(self, text: str) -> np.ndarray:
        return self._embed([text], "RETRIEVAL_QUERY")[0]


def get_embedder(backend: str) -> Embedder:
    if backend == "tfidf":
        return TfidfEmbedder()
    if backend == "gemini":
        return GeminiEmbedder()
    raise ValueError(f"Unknown embedding backend: {backend!r}. Use 'tfidf' or 'gemini'.")
