from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.trace.repository import TraceRepository

router = APIRouter()


@router.get("/traces/{trace_id}")
def get_trace(trace_id: str, db: Session = Depends(get_db)) -> dict:
    trace = TraceRepository(db).get(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return trace
