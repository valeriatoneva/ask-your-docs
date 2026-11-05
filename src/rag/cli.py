"""Command line interface.

    python -m rag.cli index --docs data/docs --backend tfidf
    python -m rag.cli ask "How do signals differ from observables?"
    python -m rag.cli chat --generator gemini
"""

from __future__ import annotations

import argparse
import sys

from .pipeline import Answer, RagPipeline

DEFAULT_INDEX_DIR = "index"


def _load_env() -> None:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:  # python-dotenv is optional
        pass


def _print_answer(answer: Answer, show_sources: bool = True) -> None:
    print(f"\n{answer.text}\n")
    if show_sources:
        print("Retrieved passages:")
        for chunk, score in answer.hits:
            print(f"  - {chunk.source} (chunk {chunk.index}, similarity {score:.2f})")
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag", description="Ask Your Docs: ask questions about your own documents.")
    sub = parser.add_subparsers(dest="command", required=True)

    index = sub.add_parser("index", help="Read documents and build the search index.")
    index.add_argument("--docs", default="data/docs", help="Folder with .md/.txt files.")
    index.add_argument("--index-dir", default=DEFAULT_INDEX_DIR)
    index.add_argument("--backend", choices=["tfidf", "gemini"], default="tfidf")
    index.add_argument("--chunk-size", type=int, default=80, help="Words per chunk.")
    index.add_argument("--overlap", type=int, default=20, help="Words shared between chunks.")

    for name, help_text in (("ask", "Ask one question."), ("chat", "Ask questions interactively.")):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--index-dir", default=DEFAULT_INDEX_DIR)
        cmd.add_argument("--generator", choices=["extractive", "gemini"], default="extractive")
        cmd.add_argument("-k", type=int, default=3, help="Number of passages to retrieve.")
        if name == "ask":
            cmd.add_argument("question")
    return parser


def main(argv: list[str] | None = None) -> int:
    _load_env()
    args = build_parser().parse_args(argv)

    try:
        if args.command == "index":
            pipeline = RagPipeline.build(
                args.docs, backend=args.backend, size=args.chunk_size, overlap=args.overlap
            )
            pipeline.save(args.index_dir)
            print(f"Indexed {len(pipeline.store.chunks)} chunks with the '{args.backend}' backend -> {args.index_dir}/")
        elif args.command == "ask":
            pipeline = RagPipeline.load(args.index_dir, generator=args.generator)
            _print_answer(pipeline.ask(args.question, k=args.k))
        elif args.command == "chat":
            pipeline = RagPipeline.load(args.index_dir, generator=args.generator)
            print("Ask a question (empty line to quit).")
            while True:
                question = input("> ").strip()
                if not question:
                    break
                _print_answer(pipeline.ask(question, k=args.k))
    except (FileNotFoundError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
