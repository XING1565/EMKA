from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import select

from backend.app.core.database import SessionLocal
from backend.app.documents.models import DocumentChunkModel
from backend.app.main import app


client = TestClient(app)


def _png_bytes() -> bytes:
    image = Image.new("RGB", (12, 8), color=(255, 255, 255))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_uploaded_text_can_be_retrieved_by_chat_search_docs():
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("alpha.txt", b"project alpha risk delay owner alice", "text/plain")},
    )
    document_id = upload.json()["document_id"]

    response = client.post("/api/v1/chat", json={"message": "alpha risk delay"})

    assert response.status_code == 200
    docs = response.json()["retrieved_docs"]
    assert docs
    assert docs[0]["document_id"] == document_id
    assert docs[0]["title"] == "alpha.txt"
    assert docs[0]["modality"] == "text"
    assert "mock-doc-001" not in docs[0]["document_id"]


def test_uploaded_csv_retrieval_contains_row_range_and_chunk_embedding():
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("risk.csv", b"date,risk,owner\n2026-07-22,delay,Alice", "text/csv")},
    )
    document_id = upload.json()["document_id"]

    response = client.post("/api/v1/chat", json={"message": "delay Alice"})

    assert response.status_code == 200
    docs = response.json()["retrieved_docs"]
    table_docs = [doc for doc in docs if doc["document_id"] == document_id]
    assert table_docs
    assert table_docs[0]["modality"] == "table"
    assert table_docs[0]["row_range"] == "2-2"
    assert "rows 2-2" in table_docs[0]["citation"]

    db = SessionLocal()
    try:
        chunks = list(db.execute(select(DocumentChunkModel).where(DocumentChunkModel.document_id == document_id)).scalars())
        assert chunks
        assert chunks[0].embedding_id
    finally:
        db.close()


def test_uploaded_image_retrieval_contains_ocr_confidence():
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("screen.png", _png_bytes(), "image/png")},
    )
    document_id = upload.json()["document_id"]

    response = client.post("/api/v1/chat", json={"message": "OCR screen"})

    assert response.status_code == 200
    docs = response.json()["retrieved_docs"]
    image_docs = [doc for doc in docs if doc["document_id"] == document_id]
    assert image_docs
    assert image_docs[0]["modality"] == "image"
    assert image_docs[0]["ocr_confidence"] == 0.75
    assert "OCR confidence 0.75" in image_docs[0]["citation"]
