from sqlalchemy import inspect

from backend.app.core.database import Base, SessionLocal, init_database
from backend.app.documents.models import DocumentChunkModel, DocumentModel
from backend.app.trace.models import TraceModel


def test_sqlalchemy_metadata_contains_task_002_tables():
    init_database()

    assert {
        "users",
        "conversations",
        "memories",
        "documents",
        "document_chunks",
        "traces",
        "tool_calls",
    }.issubset(Base.metadata.tables.keys())


def test_sqlite_init_creates_tables_and_persists_json_fields():
    init_database()
    db = SessionLocal()
    try:
        inspector = inspect(db.bind)
        assert "documents" in inspector.get_table_names()
        assert "document_chunks" in inspector.get_table_names()

        document = DocumentModel(
            title="风险表",
            doc_type="risk",
            source="upload",
            modality="table",
            content="row 1: risk",
            metadata_json={"filename": "risk.csv"},
        )
        db.add(document)
        db.commit()

        chunk = DocumentChunkModel(
            document_id=document.id,
            chunk_index=0,
            content="row 1: risk",
            embedding_id="emb-1",
            metadata_json={"row_range": "1-1"},
        )
        trace = TraceModel(
            message="ingest file",
            ingestion_ops=[{"parser": "table_parser", "chunk_count": 1}],
        )
        db.add_all([chunk, trace])
        db.commit()

        saved_chunk = db.get(DocumentChunkModel, chunk.id)
        saved_trace = db.get(TraceModel, trace.id)

        assert saved_chunk.milvus_collection == "emka_document_chunks"
        assert saved_chunk.metadata_json["row_range"] == "1-1"
        assert saved_trace.ingestion_ops[0]["parser"] == "table_parser"
    finally:
        db.close()
