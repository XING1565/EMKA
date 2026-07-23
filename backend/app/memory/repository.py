from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.memory.models import MemoryModel


class MemoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_memory(
        self,
        *,
        memory_type: str,
        content: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        summary: str | None = None,
        metadata: dict | None = None,
        importance: float = 0.5,
    ) -> MemoryModel:
        memory = MemoryModel(
            user_id=user_id,
            conversation_id=conversation_id,
            memory_type=memory_type,
            content=content,
            summary=summary,
            metadata_json=metadata or {},
            importance=importance,
        )
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def list_memories(
        self,
        *,
        user_id: str | None = None,
        conversation_id: str | None = None,
        memory_type: str | None = None,
        include_global: bool = False,
        limit: int = 20,
    ) -> list[MemoryModel]:
        stmt = select(MemoryModel).order_by(MemoryModel.created_at.desc()).limit(limit)
        if memory_type:
            stmt = stmt.where(MemoryModel.memory_type == memory_type)
        if conversation_id:
            stmt = stmt.where(MemoryModel.conversation_id == conversation_id)
        if user_id and include_global:
            stmt = stmt.where(or_(MemoryModel.user_id == user_id, MemoryModel.user_id.is_(None)))
        elif user_id:
            stmt = stmt.where(MemoryModel.user_id == user_id)
        elif include_global:
            stmt = stmt.where(MemoryModel.user_id.is_(None))
        return list(self.db.execute(stmt).scalars())
