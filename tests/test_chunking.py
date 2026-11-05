import pytest

from rag.chunking import chunk_text


def test_chunks_overlap_and_cover_all_words():
    text = " ".join(f"w{i}" for i in range(100))
    chunks = chunk_text(text, "doc.md", size=40, overlap=10)

    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert chunks[0].text.split()[-10:] == chunks[1].text.split()[:10]
    # every word of the original text appears in at least one chunk
    covered = {word for c in chunks for word in c.text.split()}
    assert covered == set(text.split())


def test_short_text_gives_one_chunk():
    chunks = chunk_text("just a few words", "doc.md", size=40, overlap=10)
    assert len(chunks) == 1
    assert chunks[0].source == "doc.md"


def test_empty_text_gives_no_chunks():
    assert chunk_text("   ", "doc.md") == []


@pytest.mark.parametrize("size,overlap", [(0, 0), (10, 10), (10, -1)])
def test_invalid_parameters_raise(size, overlap):
    with pytest.raises(ValueError):
        chunk_text("some text here", "doc.md", size=size, overlap=overlap)
