import json
from pathlib import Path

import pytest

from rag.cli import main
from rag.pipeline import RagPipeline

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "docs"
QUESTIONS = json.loads((ROOT / "eval" / "questions.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def pipeline() -> RagPipeline:
    return RagPipeline.build(DOCS, backend="tfidf")


def test_retrieval_finds_the_right_document(pipeline):
    answer = pipeline.ask("Which RxJS operator should I use for typeahead search?")
    assert answer.sources[0] == "rxjs-basics.md"
    assert "[rxjs-basics.md]" in answer.text


def test_retrieval_quality_on_labelled_questions(pipeline):
    correct = 0
    for item in QUESTIONS:
        sources = [chunk.source for chunk, _ in pipeline.retrieve(item["question"], k=3)]
        correct += item["expected_source"] in sources
    assert correct / len(QUESTIONS) >= 0.8


def test_unrelated_question_gets_no_answer(pipeline):
    answer = pipeline.ask("zzzz qqqq xxxx")
    assert "don't know" in answer.text.lower()


def test_save_and_load_give_same_results(pipeline, tmp_path):
    pipeline.save(tmp_path)
    loaded = RagPipeline.load(tmp_path)
    question = "Why does server side pagination need a stable sort order?"
    assert loaded.ask(question).sources == pipeline.ask(question).sources


def test_cli_index_then_ask(tmp_path, capsys):
    index_dir = str(tmp_path / "idx")
    assert main(["index", "--docs", str(DOCS), "--index-dir", index_dir]) == 0
    assert main(["ask", "What does HTTP status 403 mean?", "--index-dir", index_dir]) == 0
    assert "rest-api-error-handling.md" in capsys.readouterr().out


def test_cli_reports_missing_index(tmp_path, capsys):
    assert main(["ask", "anything", "--index-dir", str(tmp_path / "missing")]) == 1
    assert "Error" in capsys.readouterr().err
