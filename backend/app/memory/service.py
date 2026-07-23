from sqlalchemy.orm import Session

from backend.app.memory.knowledge_memory import KnowledgeMemory
from backend.app.memory.models import MemoryModel
from backend.app.memory.repository import MemoryRepository
from backend.app.memory.session_memory import SessionMemory
from backend.app.memory.user_memory import UserMemory


class MemoryService:
    def __init__(self, db: Session):
        self.repository = MemoryRepository(db)
        self.session = SessionMemory(self.repository)
        self.user = UserMemory(self.repository)
        self.knowledge = KnowledgeMemory(self.repository)

    def load_context(self, user_id: str | None = None, conversation_id: str | None = None) -> tuple[dict, list[dict]]:
        session_items = self.session.load(conversation_id)
        user_items = self.user.load(user_id)
        knowledge_items = self.knowledge.load(user_id)
        context = {
            "session": [_serialize_memory(item) for item in session_items],
            "user": [_serialize_memory(item) for item in user_items],
            "knowledge": [_serialize_memory(item) for item in knowledge_items],
        }
        ops = [
            {"op": "read", "memory_type": "session", "count": len(session_items)},
            {"op": "read", "memory_type": "user", "count": len(user_items)},
            {"op": "read", "memory_type": "knowledge", "count": len(knowledge_items)},
        ]
        return context, ops

    def write_after_run(
        self,
        *,
        user_id: str | None,
        conversation_id: str | None,
        message: str,
        answer: str,
    ) -> list[dict]:
        ops: list[dict] = []
        if conversation_id:
            memory = self.session.save_dialogue(conversation_id, user_id, message, answer)
            ops.append({"op": "write", "memory_type": "session", "memory_id": memory.id})
        if user_id:
            memory = self.user.save_profile_note(
                user_id,
                f"Recent query: {message[:180]}",
                metadata={"source": "runtime", "kind": "recent_query"},
            )
            ops.append({"op": "write", "memory_type": "user", "memory_id": memory.id})
        return ops

    def list_memories(self, user_id: str, memory_type: str | None = None, limit: int = 20) -> list[dict]:
        items = self.repository.list_memories(user_id=user_id, memory_type=memory_type, limit=limit)
        return [_serialize_memory(item) for item in items]


def _serialize_memory(memory: MemoryModel) -> dict:
    return {
        "id": memory.id,
        "user_id": memory.user_id,
        "conversation_id": memory.conversation_id,
        "memory_type": memory.memory_type,
        "content": memory.content,
        "summary": memory.summary,
        "metadata": memory.metadata_json or {},
        "importance": memory.importance,
    }
