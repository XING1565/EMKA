from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from backend.app.core.config import get_settings

EMKA_DOCUMENT_CHUNKS_COLLECTION = "emka_document_chunks"
DEFAULT_EMBEDDING_DIMENSION = 1536


@dataclass
class VectorHit:
    embedding_id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemoryVectorStore:
    def __init__(
        self,
        collection_name: str = EMKA_DOCUMENT_CHUNKS_COLLECTION,
        dimension: int = DEFAULT_EMBEDDING_DIMENSION,
    ) -> None:
        self.collection_name = collection_name
        self.dimension = dimension
        self._ready = False
        self._vectors: dict[str, tuple[list[float], dict[str, Any]]] = {}

    def ensure_collection(self) -> bool:
        self._ready = True
        return True

    def insert_chunk_vector(self, embedding_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> bool:
        self._validate_vector(vector)
        self.ensure_collection()
        self._vectors[embedding_id] = (list(vector), dict(metadata or {}))
        return True

    def search(self, query_vector: list[float], top_k: int = 5) -> list[VectorHit]:
        self._validate_vector(query_vector)
        self.ensure_collection()
        hits = [
            VectorHit(embedding_id=embedding_id, score=_cosine_similarity(query_vector, vector), metadata=metadata)
            for embedding_id, (vector, metadata) in self._vectors.items()
        ]
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]

    def clear(self) -> None:
        self._vectors.clear()
        self._ready = False

    def _validate_vector(self, vector: list[float]) -> None:
        if len(vector) != self.dimension:
            raise ValueError(f"expected vector dimension {self.dimension}, got {len(vector)}")


class MilvusVectorStore:
    def __init__(
        self,
        uri: str,
        collection_name: str = EMKA_DOCUMENT_CHUNKS_COLLECTION,
        dimension: int = DEFAULT_EMBEDDING_DIMENSION,
    ) -> None:
        self.uri = uri
        self.collection_name = collection_name
        self.dimension = dimension
        try:
            from pymilvus import DataType, MilvusClient
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError("pymilvus is not available") from exc
        self._data_type = DataType
        self._client = MilvusClient(uri=uri)

    def ensure_collection(self) -> bool:
        if self._client.has_collection(self.collection_name):
            return True
        schema = self._client.create_schema(auto_id=False, enable_dynamic_field=True)
        schema.add_field(field_name="embedding_id", datatype=self._data_type.VARCHAR, is_primary=True, max_length=128)
        schema.add_field(field_name="vector", datatype=self._data_type.FLOAT_VECTOR, dim=self.dimension)
        index_params = self._client.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="COSINE")
        self._client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )
        return True

    def insert_chunk_vector(self, embedding_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> bool:
        self.ensure_collection()
        row = {"embedding_id": embedding_id, "vector": vector, **(metadata or {})}
        self._client.insert(collection_name=self.collection_name, data=[row])
        return True

    def search(self, query_vector: list[float], top_k: int = 5) -> list[VectorHit]:
        self.ensure_collection()
        results = self._client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            anns_field="vector",
            limit=top_k,
            output_fields=["embedding_id"],
        )
        hits: list[VectorHit] = []
        for result in results[0] if results else []:
            entity = result.get("entity", {}) if isinstance(result, dict) else {}
            hits.append(
                VectorHit(
                    embedding_id=str(entity.get("embedding_id") or result.get("id")),
                    score=float(result.get("distance", 0.0)),
                    metadata=dict(entity),
                )
            )
        return hits


def build_vector_store():
    settings = get_settings()
    collection_name = settings.milvus_collection or EMKA_DOCUMENT_CHUNKS_COLLECTION
    dimension = settings.embedding_dimension or DEFAULT_EMBEDDING_DIMENSION
    if settings.milvus_uri:
        try:
            return MilvusVectorStore(settings.milvus_uri, collection_name, dimension)
        except Exception:
            pass
    return InMemoryVectorStore(collection_name, dimension)


_SHARED_VECTOR_STORE = None


def get_vector_store():
    global _SHARED_VECTOR_STORE
    if _SHARED_VECTOR_STORE is None:
        _SHARED_VECTOR_STORE = build_vector_store()
    return _SHARED_VECTOR_STORE


def reset_vector_store() -> None:
    global _SHARED_VECTOR_STORE
    _SHARED_VECTOR_STORE = build_vector_store()


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)
