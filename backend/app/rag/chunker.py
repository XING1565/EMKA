from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    chunk_index: int
    content: str
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


def chunk_text(content: str, metadata: dict[str, Any] | None = None, max_tokens: int = 120) -> list[Chunk]:
    base_metadata = dict(metadata or {})
    tokens = (content or "").split()
    if not tokens:
        return [Chunk(chunk_index=0, content="", token_count=0, metadata=base_metadata)]

    chunks: list[Chunk] = []
    for index, start in enumerate(range(0, len(tokens), max_tokens)):
        chunk_metadata = dict(base_metadata)
        row_ranges = chunk_metadata.get("row_ranges") or []
        if row_ranges and "row_range" not in chunk_metadata:
            chunk_metadata["row_range"] = row_ranges[min(index, len(row_ranges) - 1)]
        part_tokens = tokens[start : start + max_tokens]
        chunks.append(
            Chunk(
                chunk_index=index,
                content=" ".join(part_tokens),
                token_count=len(part_tokens),
                metadata=chunk_metadata,
            )
        )
    return chunks
