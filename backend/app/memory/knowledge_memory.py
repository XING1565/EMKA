from backend.app.memory.models import MemoryModel
from backend.app.memory.repository import MemoryRepository


class KnowledgeMemory:
    memory_type = "knowledge"
    importance = 0.8

    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def save_knowledge(self, content: str, user_id: str | None = None, metadata: dict | None = None) -> MemoryModel:
        return self.repository.create_memory(
            memory_type=self.memory_type,
            user_id=user_id,
            content=content,
            summary=content[:160],
            metadata=metadata or {"source": "manual"},
            importance=self.importance,
        )

    def load(self, user_id: str | None = None, limit: int = 5) -> list[MemoryModel]:
        return self.repository.list_memories(
            user_id=user_id,
            memory_type=self.memory_type,
            include_global=True,
            limit=limit,
        )
