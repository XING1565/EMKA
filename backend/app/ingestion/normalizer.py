from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class NormalizedContent:
    content: str
    metadata: dict = field(default_factory=dict)


def normalize_content(content: str, metadata: dict) -> NormalizedContent:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.strip() for line in normalized.split("\n"))
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    if not normalized:
        normalized = "No normalized text was extracted."
    out_metadata = dict(metadata)
    out_metadata["normalized"] = True
    out_metadata["char_count"] = len(normalized)
    return NormalizedContent(content=normalized, metadata=out_metadata)
