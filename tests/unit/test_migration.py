from pathlib import Path


def test_init_migration_contains_task_002_tables_and_columns():
    sql = Path("EMKA/database/migrations/001_init.sql").read_text(encoding="utf-8").lower()

    for table in [
        "users",
        "conversations",
        "memories",
        "documents",
        "document_chunks",
        "traces",
        "tool_calls",
    ]:
        assert f"create table if not exists {table}" in sql

    assert "create extension if not exists pgcrypto" in sql
    assert "modality varchar(32)" in sql
    assert "ingestion_ops jsonb" in sql
    assert "emka_document_chunks" in sql
    assert "create index if not exists" in sql
