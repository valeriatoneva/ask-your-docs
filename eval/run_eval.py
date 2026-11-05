"""Measure how good retrieval is on a small labelled question set.

Metrics
-------
hit@k : share of questions where the expected document is among the top-k retrieved chunks.
MRR   : mean reciprocal rank of the first correct chunk (1.0 = always ranked first).

Usage:
    python eval/run_eval.py --backend tfidf
    python eval/run_eval.py --backend gemini     # needs GEMINI_API_KEY
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from rag.pipeline import RagPipeline  # noqa: E402


def evaluate(pipeline: RagPipeline, questions: list[dict], k: int) -> dict:
    hits = 0
    reciprocal_ranks: list[float] = []
    failures: list[dict] = []

    for item in questions:
        retrieved = pipeline.retrieve(item["question"], k=k)
        sources = [chunk.source for chunk, _ in retrieved]
        if item["expected_source"] in sources:
            hits += 1
            reciprocal_ranks.append(1.0 / (sources.index(item["expected_source"]) + 1))
        else:
            reciprocal_ranks.append(0.0)
            failures.append({"question": item["question"], "expected": item["expected_source"], "got": sources})

    total = len(questions)
    return {
        "questions": total,
        "k": k,
        f"hit@{k}": hits / total,
        "mrr": sum(reciprocal_ranks) / total,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate retrieval quality.")
    parser.add_argument("--docs", default=str(ROOT / "data" / "docs"))
    parser.add_argument("--questions", default=str(ROOT / "eval" / "questions.json"))
    parser.add_argument("--backend", choices=["tfidf", "gemini"], default="tfidf")
    parser.add_argument("-k", type=int, default=3)
    args = parser.parse_args()

    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    questions = json.loads(Path(args.questions).read_text(encoding="utf-8"))
    pipeline = RagPipeline.build(args.docs, backend=args.backend)
    result = evaluate(pipeline, questions, args.k)

    print(f"Backend: {args.backend}")
    print(f"Questions: {result['questions']}")
    print(f"hit@{args.k}: {result[f'hit@{args.k}']:.2f}")
    print(f"MRR:   {result['mrr']:.2f}")
    for failure in result["failures"]:
        print(f"  MISS: {failure['question']} (expected {failure['expected']}, got {failure['got']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
