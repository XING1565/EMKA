from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.runtime.models import RuntimeRequest, RuntimeResponse
from backend.app.runtime.orchestrator import RuntimeOrchestrator

router = APIRouter()


@router.post("/chat", response_model=RuntimeResponse)
async def chat(payload: RuntimeRequest, db: Session = Depends(get_db)) -> RuntimeResponse:
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="message empty")
    orchestrator = RuntimeOrchestrator(db)
    try:
        return await orchestrator.run(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="runtime execution failed") from exc
