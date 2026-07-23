from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.core.vector_store import EMKA_DOCUMENT_CHUNKS_COLLECTION, get_vector_store
from backend.app.documents.models import DocumentChunkModel, DocumentModel
from backend.app.rag.chunker import chunk_text
from backend.app.rag.embeddings import DeterministicEmbeddingService
from backend.app.rag.retriever import Retriever


class RAGPipeline:
    def __init__(self, db: Session, embedding_service: DeterministicEmbeddingService | None = None):
        self.db = db
        self.embedding_service = embedding_service or DeterministicEmbeddingService()
        self.vector_store = get_vector_store()

    def index_document(self, document: DocumentModel) -> dict:
        chunks = chunk_text(document.content, document.metadata_json or {})
        indexed = True
        for chunk in chunks:
            embedding_id = f"emb-{uuid4()}"
            model = DocumentChunkModel(
                document_id=document.id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                token_count=chunk.token_count,
                embedding_id=embedding_id,
                milvus_collection=EMKA_DOCUMENT_CHUNKS_COLLECTION,
                metadata_json=chunk.metadata,
            )
            self.db.add(model)
            try:
                self.vector_store.insert_chunk_vector(
                    embedding_id,
                    self.embedding_service.embed(chunk.content),
                    {
                        "document_id": document.id,
                        "chunk_index": chunk.chunk_index,
                        "modality": document.modality,
                    },
                )
            except Exception:
                indexed = False
        self.db.commit()
        return {"chunk_count": len(chunks), "indexed": indexed}

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        return Retriever(self.db, self.embedding_service).search(query, top_k=top_k)
