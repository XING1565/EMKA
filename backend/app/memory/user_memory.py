from backend.app.memory.models import MemoryModel
from backend.app.memory.repository import MemoryRepository


class UserMemory:
    memory_type = "user"
    importance = 0.7

    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def save_profile_note(self, user_id: str, content: str, metadata: dict | None = None) -> MemoryModel:
        return self.repository.create_memory(
            memory_type=self.memory_type,
            user_id=user_id,
            content=content,
            summary=content[:160],
            metadata=metadata or {"source": "runtime"},
            importance=self.importance,
        )

    def load(self, user_id: str | None, limit: int = 5) -> list[MemoryModel]:
        if not user_id:
            return []
        return self.repository.list_memories(
            user_id=user_id,
            memory_type=self.memory_type,
            limit=limit,
        )
