from backend.app.memory.models import MemoryModel
from backend.app.memory.repository import MemoryRepository


class SessionMemory:
    memory_type = "session"
    importance = 0.5

    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def save_dialogue(self, conversation_id: str, user_id: str | None, message: str, answer: str) -> MemoryModel:
        return self.repository.create_memory(
            memory_type=self.memory_type,
            user_id=user_id,
            conversation_id=conversation_id,
            content=f"User: {message}\nAssistant: {answer}",
            summary=f"Dialogue about: {message[:120]}",
            metadata={"source": "runtime"},
            importance=self.importance,
        )

    def load(self, conversation_id: str | None, limit: int = 5) -> list[MemoryModel]:
        if not conversation_id:
            return []
        return self.repository.list_memories(
            conversation_id=conversation_id,
            memory_type=self.memory_type,
            limit=limit,
        )
