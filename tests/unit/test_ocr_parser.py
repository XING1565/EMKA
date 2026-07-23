from io import BytesIO

from PIL import Image

from backend.app.ingestion.ocr_parser import parse_image_file


def _png_bytes() -> bytes:
    image = Image.new("RGB", (12, 8), color=(255, 255, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_ocr_parser_returns_mock_text_and_image_metadata():
    metadata = {}

    text = parse_image_file("screen.png", _png_bytes(), metadata)

    assert text == "OCR text extracted from screen.png"
    assert metadata["ocr_confidence"] == 0.75
    assert metadata["image_width"] == 12
    assert metadata["image_height"] == 8
    assert metadata["image_format"] == "PNG"


def test_ocr_parser_falls_back_for_invalid_image_bytes():
    metadata = {}

    text = parse_image_file("bad.png", b"not an image", metadata)

    assert "fallback" in text
    assert metadata["ocr_confidence"] == 0.0
    assert "parse_error" in metadata
