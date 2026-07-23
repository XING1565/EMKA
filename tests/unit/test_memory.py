from backend.app.core.database import SessionLocal, init_database
from backend.app.memory.service import MemoryService


def test_session_user_and_knowledge_memory_can_be_saved_and_loaded():
    init_database()
    db = SessionLocal()
    try:
        service = MemoryService(db)

        session_memory = service.session.save_dialogue(
            conversation_id="conv-1",
            user_id="user-1",
            message="hello",
            answer="hi",
        )
        user_memory = service.user.save_profile_note(
            user_id="user-1",
            content="User prefers risk reports",
            metadata={"common_material_type": "risk_table"},
        )
        knowledge_memory = service.knowledge.save_knowledge(
            content="Risk tables usually contain owner and due date columns.",
            metadata={"modality": "table"},
        )

        assert session_memory.memory_type == "session"
        assert session_memory.importance == 0.5
        assert user_memory.memory_type == "user"
        assert user_memory.importance == 0.7
        assert knowledge_memory.memory_type == "knowledge"
        assert knowledge_memory.importance == 0.8

        context, ops = service.load_context(user_id="user-1", conversation_id="conv-1")

        assert len(context["session"]) == 1
        assert len(context["user"]) == 1
        assert len(context["knowledge"]) == 1
        assert {op["memory_type"] for op in ops} == {"session", "user", "knowledge"}
    finally:
        db.close()


def test_memory_service_write_after_run_returns_memory_ops():
    init_database()
    db = SessionLocal()
    try:
        service = MemoryService(db)

        ops = service.write_after_run(
            user_id="user-2",
            conversation_id="conv-2",
            message="analyze risks",
            answer="done",
        )

        assert [op["memory_type"] for op in ops] == ["session", "user"]
        assert all(op["op"] == "write" for op in ops)

        listed = service.list_memories("user-2")
        assert len(listed) >= 2
    finally:
        db.close()
