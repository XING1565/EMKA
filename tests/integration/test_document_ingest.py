from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_upload_supported_file_types_and_list_modalities():
    cases = [
        ("note.txt", b"plain text", "text"),
        ("readme.md", b"# Heading", "text"),
        ("report.pdf", b"%PDF-1.4 fake", "text"),
        ("brief.docx", b"PK fake docx", "text"),
        ("risk.csv", b"date,risk,owner\n2026-07-22,late,Alice", "table"),
        ("sheet.xlsx", b"PK fake xlsx", "table"),
        ("screen.png", b"\x89PNG fake", "image"),
        ("photo.jpg", b"\xff\xd8 fake", "image"),
    ]

    created = []
    for filename, content, modality in cases:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": (filename, content, "application/octet-stream")},
            data={"doc_type": "test"},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["document_id"]
        assert payload["title"] == filename
        assert payload["modality"] == modality
        assert not payload["parser"].startswith("placeholder")
        assert payload["chunk_count"] == 1
        assert payload["indexed"] is True
        created.append(payload)

    list_response = client.get("/api/v1/documents", params={"limit": 20})
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    seen = {item["title"]: item["modality"] for item in items}
    for payload in created:
        assert seen[payload["title"]] == payload["modality"]


def test_upload_empty_file_returns_400():
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )

    assert response.status_code == 400


def test_upload_unsupported_file_returns_422():
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("archive.zip", b"zip", "application/zip")},
    )

    assert response.status_code == 422


def test_get_document_returns_content_and_metadata():
    upload_response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("risk.csv", b"date,risk\n2026-07-22,delay", "text/csv")},
    )
    document_id = upload_response.json()["document_id"]

    response = client.get(f"/api/v1/documents/{document_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == document_id
    assert payload["modality"] == "table"
    assert "Table summary (csv): 1 data rows" in payload["content"]
    assert "row 2: date=2026-07-22; risk=delay" in payload["content"]
    assert payload["metadata"]["parser"] == "table_parser"
    assert payload["metadata"]["table_columns"] == ["date", "risk"]
    assert payload["metadata"]["normalized"] is True
