"""Produce the final answer from the retrieved chunks.

* ``GeminiGenerator``      - an LLM writes the answer, using only the retrieved text.
* ``ExtractiveGenerator``  - no LLM: returns the best matching passage (works offline).
"""

from __future__ import annotations

import os
from typing import Protocol

from .chunking import Chunk

PROMPT_TEMPLATE = """You answer questions using ONLY the context below.
- If the context does not contain the answer, say: "I don't know based on the provided documents."
- Be concise (at most 4 sentences).
- After the answer, list the sources you used in square brackets, for example [angular-signals.md].

Context:
{context}

Question: {question}

Answer:"""


def build_prompt(question: str, hits: list[tuple[Chunk, float]]) -> str:
    context = "\n\n".join(f"[{chunk.source}]\n{chunk.text}" for chunk, _ in hits)
    return PROMPT_TEMPLATE.format(context=context, question=question)


class Generator(Protocol):
    name: str

    def generate(self, question: str, hits: list[tuple[Chunk, float]]) -> str: ...


class ExtractiveGenerator:
    name = "extractive"

    def generate(self, question: str, hits: list[tuple[Chunk, float]]) -> str:
        if not hits or hits[0][1] <= 0:
            return "I don't know based on the provided documents."
        best, _ = hits[0]
        return f"{best.text}\n\n[{best.source}]"


class GeminiGenerator:
    name = "gemini"

    def __init__(self, model: str | None = None) -> None:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Copy .env.example to .env and add your key.")
        self._client = genai.Client(api_key=api_key)
        self._model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def generate(self, question: str, hits: list[tuple[Chunk, float]]) -> str:
        response = self._client.models.generate_content(model=self._model, contents=build_prompt(question, hits))
        return (response.text or "").strip()


def get_generator(name: str) -> Generator:
    if name == "extractive":
        return ExtractiveGenerator()
    if name == "gemini":
        return GeminiGenerator()
    raise ValueError(f"Unknown generator: {name!r}. Use 'extractive' or 'gemini'.")
