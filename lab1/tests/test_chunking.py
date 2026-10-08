import pytest

from src.preprocessing.chunking import chunk_document, parse_blocks, split_fixed

WORDS = " ".join(f"word{i}" for i in range(400))

DOC_TEXT = """Intro paragraph about pods.

## Lifecycle

Pods go through phases.

### Phases

Pending, Running, Succeeded.

## Empty section

### Child

Child text.

```yaml
kind: Pod

metadata:
  name: demo
```
"""


def make_doc(text: str = DOC_TEXT) -> dict:
    return {
        "document_id": "concepts/pods.md",
        "title": "Pods",
        "url": "https://kubernetes.io/docs/concepts/pods/",
        "source": "kubernetes-docs",
        "section": "concepts",
        "updated_at": "2026-10-07T00:00:00+00:00",
        "text": text,
    }


def test_split_fixed_respects_size_and_word_boundaries():
    pieces = split_fixed(WORDS, size=100)
    vocabulary = set(WORDS.split())
    assert all(len(piece) <= 100 for _, piece in pieces)
    assert all(set(piece.split()) <= vocabulary for _, piece in pieces)
    assert " ".join(piece for _, piece in pieces) == WORDS  # без overlap текст покрыт ровно один раз


def test_split_fixed_overlap_repeats_tail_of_previous_piece():
    pieces = [piece for _, piece in split_fixed(WORDS, size=100, overlap=30)]
    assert len(pieces) > len(split_fixed(WORDS, size=100))
    for previous, current in zip(pieces, pieces[1:]):
        assert current.split()[0] in previous.split()
        assert set(current.split()) <= set(WORDS.split())


@pytest.mark.parametrize(("size", "overlap"), [(0, 0), (100, 100), (100, -1)])
def test_split_fixed_rejects_invalid_params(size, overlap):
    with pytest.raises(ValueError):
        split_fixed(WORDS, size, overlap)


def test_parse_blocks_tracks_heading_path_and_keeps_code_whole():
    blocks = parse_blocks(DOC_TEXT, "Pods")
    paths = {block.text.split("\n")[0]: block.path for block in blocks}
    assert paths["Intro paragraph about pods."] == ("Pods",)
    assert paths["Pending, Running, Succeeded."] == ("Pods", "Lifecycle", "Phases")
    assert paths["Child text."] == ("Pods", "Empty section", "Child")
    code = [block for block in blocks if block.text.startswith("```")]
    assert len(code) == 1 and "metadata:" in code[0].text  # пустая строка в коде не делит блок


def test_heading_strategy_one_section_per_chunk_with_path_prefix():
    chunks = chunk_document(make_doc(), "heading", chunk_size=1000)
    headings = [chunk["heading"] for chunk in chunks]
    assert headings == ["Pods", "Pods > Lifecycle", "Pods > Lifecycle > Phases", "Pods > Empty section > Child"]
    assert chunks[2]["text"] == "Pods > Lifecycle > Phases\n\nPending, Running, Succeeded."


def test_heading_strategy_splits_large_section():
    doc = make_doc(f"## Big\n\n{WORDS}")
    chunks = chunk_document(doc, "heading", chunk_size=300, include_heading=False)
    assert len(chunks) > 1
    assert all(len(chunk["text"]) <= 300 and chunk["heading"] == "Pods > Big" for chunk in chunks)


def test_paragraph_strategy_never_splits_small_paragraphs():
    paragraphs = [f"Paragraph {i} " + "x" * 80 for i in range(10)]
    chunks = chunk_document(make_doc("\n\n".join(paragraphs)), "paragraph", chunk_size=300, include_heading=False)
    assert all(len(chunk["text"]) <= 300 for chunk in chunks)
    joined = [part for chunk in chunks for part in chunk["text"].split("\n\n")]
    assert joined == paragraphs


def test_paragraph_strategy_moves_trailing_heading_to_next_chunk():
    text = "a" * 250 + "\n\n## Next\n\n" + "b" * 100
    chunks = chunk_document(make_doc(text), "paragraph", chunk_size=270, include_heading=False)
    assert [chunk["text"] for chunk in chunks] == ["a" * 250, "## Next\n\n" + "b" * 100]
    assert chunks[1]["heading"] == "Pods > Next"


def test_fixed_strategy_with_and_without_heading_prefix():
    with_heading = chunk_document(make_doc(), "fixed", chunk_size=60, chunk_overlap=10)
    without = chunk_document(make_doc(), "fixed", chunk_size=60, chunk_overlap=10, include_heading=False)
    assert len(with_heading) == len(without) > 1
    assert all(chunk["text"].startswith(chunk["heading"] + "\n\n") for chunk in with_heading)
    assert all(len(chunk["text"]) <= 60 for chunk in without)


def test_chunks_inherit_document_metadata_and_have_unique_ids():
    chunks = chunk_document(make_doc(), "paragraph", chunk_size=80)
    assert len({chunk["chunk_id"] for chunk in chunks}) == len(chunks)
    assert chunks[0]["chunk_id"] == "concepts/pods.md#0"
    for chunk in chunks:
        assert chunk["document_id"] == "concepts/pods.md"
        assert chunk["url"] == "https://kubernetes.io/docs/concepts/pods/"
        assert (chunk["title"], chunk["source"], chunk["section"]) == ("Pods", "kubernetes-docs", "concepts")


def test_unknown_strategy_rejected():
    with pytest.raises(ValueError):
        chunk_document(make_doc(), "semantic", chunk_size=100)
