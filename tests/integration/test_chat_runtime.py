from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_runtime_returns_trace_and_plan():
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("chat-risk.csv", b"date,risk,owner\n2026-07-22,delay,Alice", "text/csv")},
    )
    assert upload.status_code == 200

    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "chat-user-1",
            "conversation_id": "chat-conv-1",
            "message": "结合项目周报表 delay Alice，生成一份风险报告",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"]
    assert data["trace_id"]
    assert data["route"]["intent"] in {"generate_report", "multimodal_analysis"}
    assert [step["tool"] for step in data["plan"]] == ["search_docs", "summarize", "generate_report"]
    assert data["tool_calls"]
    assert data["retrieved_docs"]
    assert data["memory_ops"]

    trace_response = client.get(f"/api/v1/traces/{data['trace_id']}")
    assert trace_response.status_code == 200
    trace = trace_response.json()
    assert trace["id"] == data["trace_id"]
    assert trace["tool_calls"]
    assert trace["memory_ops"]

    memories_response = client.get("/api/v1/memories", params={"user_id": "chat-user-1"})
    assert memories_response.status_code == 200
    memories = memories_response.json()["items"]
    assert any(item["memory_type"] == "session" for item in memories)
    assert any(item["memory_type"] == "user" for item in memories)


def test_chat_empty_message_returns_400():
    response = client.post("/api/v1/chat", json={"message": "   "})

    assert response.status_code == 400
