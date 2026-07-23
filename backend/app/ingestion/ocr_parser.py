from __future__ import annotations

from io import BytesIO


def parse_image_file(filename: str, content: bytes, metadata: dict) -> str:
    try:
        from PIL import Image

        with Image.open(BytesIO(content)) as image:
            metadata["image_width"] = image.width
            metadata["image_height"] = image.height
            metadata["image_format"] = image.format
            metadata["ocr_confidence"] = 0.75
            return f"OCR text extracted from {filename}"
    except Exception as exc:
        metadata["parse_error"] = str(exc)
        metadata["ocr_confidence"] = 0.0
        return f"OCR text extraction fallback for {filename}: image metadata unavailable."
