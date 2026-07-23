from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.documents.models import DocumentChunkModel, DocumentModel


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        *,
        title: str,
        doc_type: str,
        source: str,
        modality: str,
        content: str,
        summary: str | None = None,
        metadata: dict | None = None,
        uploaded_by: str | None = None,
    ) -> DocumentModel:
        document = DocumentModel(
            title=title,
            doc_type=doc_type,
            source=source,
            modality=modality,
            content=content,
            summary=summary,
            metadata_json=metadata or {},
            uploaded_by=uploaded_by,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list_documents(
        self,
        *,
        user_id: str | None = None,
        doc_type: str | None = None,
        modality: str | None = None,
        limit: int = 20,
    ) -> list[DocumentModel]:
        stmt = select(DocumentModel).order_by(DocumentModel.created_at.desc()).limit(limit)
        if user_id:
            stmt = stmt.where(DocumentModel.uploaded_by == user_id)
        if doc_type:
            stmt = stmt.where(DocumentModel.doc_type == doc_type)
        if modality:
            stmt = stmt.where(DocumentModel.modality == modality)
        return list(self.db.execute(stmt).scalars())

    def get_document(self, document_id: str) -> DocumentModel | None:
        return self.db.get(DocumentModel, document_id)

    def create_chunks(self, chunks: list[DocumentChunkModel]) -> list[DocumentChunkModel]:
        self.db.add_all(chunks)
        self.db.commit()
        for chunk in chunks:
            self.db.refresh(chunk)
        return chunks

    def list_chunks_by_document(self, document_id: str) -> list[DocumentChunkModel]:
        stmt = select(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id).order_by(DocumentChunkModel.chunk_index.asc())
        return list(self.db.execute(stmt).scalars())
