from backend.app.rag.chunker import chunk_text


def test_chunker_splits_and_preserves_metadata():
    chunks = chunk_text("one two three four", {"modality": "table", "row_ranges": ["2-3"]}, max_tokens=2)

    assert len(chunks) == 2
    assert chunks[0].content == "one two"
    assert chunks[0].token_count == 2
    assert chunks[0].metadata["row_range"] == "2-3"


def test_chunker_handles_empty_text():
    chunks = chunk_text("", {"modality": "text"})

    assert len(chunks) == 1
    assert chunks[0].content == ""
    assert chunks[0].metadata["modality"] == "text"
