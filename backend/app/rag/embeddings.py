from __future__ import annotations

import hashlib
import math
import re

from backend.app.core.config import get_settings


class DeterministicEmbeddingService:
    def __init__(self, dimension: int | None = None) -> None:
        self.dimension = dimension or get_settings().embedding_dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = re.findall(r"[\w\u4e00-\u9fff]+", (text or "").lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            vector[index] += 1.0 + (digest[4] / 255.0)
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]
