from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.app.core.identity import ensure_user
from backend.app.documents.models import DocumentModel
from backend.app.documents.repository import DocumentRepository
from backend.app.ingestion.service import IngestionService
from backend.app.rag.pipeline import RAGPipeline


@dataclass
class UploadedDocumentResult:
    document_id: str
    title: str
    modality: str
    parser: str
    chunk_count: int
    indexed: bool


class DocumentService:
    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)
        self.ingestion = IngestionService()

    def upload(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        user_id: str | None = None,
        doc_type: str = "general",
    ) -> UploadedDocumentResult:
        ingested = self.ingestion.ingest(filename, content, content_type)
        uploaded_by = ensure_user(self.repository.db, user_id)
        document = self.repository.create_document(
            title=ingested.title,
            doc_type=doc_type or "general",
            source="upload",
            modality=ingested.modality,
            content=ingested.content,
            metadata=ingested.metadata,
            uploaded_by=uploaded_by,
        )
        rag_result = RAGPipeline(self.repository.db).index_document(document)
        return UploadedDocumentResult(
            document_id=document.id,
            title=document.title,
            modality=document.modality,
            parser=ingested.parser,
            chunk_count=rag_result["chunk_count"],
            indexed=rag_result["indexed"],
        )

    def list_documents(
        self,
        *,
        user_id: str | None = None,
        doc_type: str | None = None,
        modality: str | None = None,
        limit: int = 20,
    ) -> list[DocumentModel]:
        return self.repository.list_documents(
            user_id=user_id,
            doc_type=doc_type,
            modality=modality,
            limit=limit,
        )

    def get_document(self, document_id: str) -> DocumentModel | None:
        return self.repository.get_document(document_id)
