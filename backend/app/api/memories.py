from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.memory.service import MemoryService

router = APIRouter()


@router.get("/memories")
def list_memories(
    user_id: str = Query(...),
    memory_type: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    if memory_type and memory_type not in {"session", "user", "knowledge"}:
        raise HTTPException(status_code=422, detail="unsupported memory_type")
    return {"items": MemoryService(db).list_memories(user_id=user_id, memory_type=memory_type, limit=limit)}
