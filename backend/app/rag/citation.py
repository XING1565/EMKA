from __future__ import annotations

from typing import Any


def build_citation(title: str, chunk_index: int, modality: str, metadata: dict[str, Any] | None = None) -> str:
    metadata = metadata or {}
    base = f"{title}#chunk-{chunk_index + 1}"
    if modality == "table" and metadata.get("row_range"):
        return f"{base} rows {metadata['row_range']}"
    if modality == "image" and metadata.get("ocr_confidence") is not None:
        return f"{base} OCR confidence {metadata['ocr_confidence']}"
    return base


def citation_source_fields(modality: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = metadata or {}
    if modality == "table" and metadata.get("row_range"):
        return {"row_range": metadata["row_range"]}
    if modality == "image" and metadata.get("ocr_confidence") is not None:
        return {"ocr_confidence": metadata["ocr_confidence"]}
    return {}
