from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.documents.models import DocumentModel
from backend.app.documents.service import DocumentService
from backend.app.ingestion.detector import UnsupportedFileTypeError
from backend.app.ingestion.service import EmptyFileError

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str | None = Form(default=None),
    doc_type: str = Form(default="general"),
    db: Session = Depends(get_db),
) -> dict:
    service = DocumentService(db)
    try:
        content = await file.read()
        result = service.upload(
            filename=file.filename or "uploaded",
            content=content,
            content_type=file.content_type,
            user_id=user_id,
            doc_type=doc_type,
        )
    except EmptyFileError as exc:
        raise HTTPException(status_code=400, detail="empty file") from exc
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "document_id": result.document_id,
        "title": result.title,
        "modality": result.modality,
        "parser": result.parser,
        "chunk_count": result.chunk_count,
        "indexed": result.indexed,
    }


@router.get("/documents")
def list_documents(
    user_id: str | None = None,
    doc_type: str | None = None,
    modality: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    service = DocumentService(db)
    documents = service.list_documents(
        user_id=user_id,
        doc_type=doc_type,
        modality=modality,
        limit=limit,
    )
    return {"items": [_to_list_item(document) for document in documents]}


@router.get("/documents/{document_id}")
def get_document(document_id: str, db: Session = Depends(get_db)) -> dict:
    document = DocumentService(db).get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return {
        "id": document.id,
        "title": document.title,
        "modality": document.modality,
        "content": document.content,
        "summary": document.summary,
        "metadata": document.metadata_json or {},
    }


def _to_list_item(document: DocumentModel) -> dict:
    return {
        "id": document.id,
        "title": document.title,
        "doc_type": document.doc_type,
        "modality": document.modality,
        "summary": document.summary,
    }
