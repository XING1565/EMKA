from backend.app.rag.citation import build_citation, citation_source_fields


def test_table_citation_includes_row_range():
    metadata = {"row_range": "2-4"}

    assert build_citation("risk.csv", 0, "table", metadata) == "risk.csv#chunk-1 rows 2-4"
    assert citation_source_fields("table", metadata) == {"row_range": "2-4"}


def test_image_citation_includes_ocr_confidence():
    metadata = {"ocr_confidence": 0.75}

    assert build_citation("screen.png", 1, "image", metadata) == "screen.png#chunk-2 OCR confidence 0.75"
    assert citation_source_fields("image", metadata) == {"ocr_confidence": 0.75}
