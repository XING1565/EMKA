from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.vector_store import get_vector_store
from backend.app.documents.models import DocumentChunkModel, DocumentModel
from backend.app.rag.citation import build_citation, citation_source_fields
from backend.app.rag.embeddings import DeterministicEmbeddingService


class Retriever:
    def __init__(self, db: Session, embedding_service: DeterministicEmbeddingService | None = None):
        self.db = db
        self.embedding_service = embedding_service or DeterministicEmbeddingService()
        self.vector_store = get_vector_store()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        hits = self.vector_store.search(self.embedding_service.embed(query), top_k=top_k)
        results: list[dict] = []
        seen: set[str] = set()
        for hit in hits:
            chunk = self._chunk_for_embedding(hit.embedding_id)
            if chunk is None or chunk.id in seen:
                continue
            document = self.db.get(DocumentModel, chunk.document_id)
            if document is None:
                continue
            seen.add(chunk.id)
            metadata = chunk.metadata_json or {}
            results.append(
                {
                    "document_id": document.id,
                    "title": document.title,
                    "modality": document.modality,
                    "score": hit.score,
                    "citation": build_citation(document.title, chunk.chunk_index, document.modality, metadata),
                    "snippet": chunk.content[:500],
                    **citation_source_fields(document.modality, metadata),
                }
            )
        return results

    def _chunk_for_embedding(self, embedding_id: str) -> DocumentChunkModel | None:
        stmt = select(DocumentChunkModel).where(DocumentChunkModel.embedding_id == embedding_id)
        return self.db.execute(stmt).scalars().first()
