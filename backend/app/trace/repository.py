from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.runtime.models import RuntimeRequest, ToolResult
from backend.app.trace.models import ToolCallModel, TraceModel


class TraceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, request: RuntimeRequest) -> str:
        trace_id = str(uuid4())
        trace = TraceModel(
            id=trace_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            message=request.message,
            status="running",
        )
        self.db.add(trace)
        self.db.commit()
        return trace_id

    def update(self, trace_id: str, **fields) -> None:
        trace = self.db.get(TraceModel, trace_id)
        if trace is None:
            return
        for key, value in fields.items():
            setattr(trace, key, value)
        self.db.commit()

    def add_tool_call(self, trace_id: str, tool_name: str, params: dict, result: ToolResult) -> dict:
        payload = result.model_dump()
        call = ToolCallModel(
            id=str(uuid4()),
            trace_id=trace_id,
            tool_name=tool_name,
            params=params,
            result=payload,
            success=result.success,
            error=result.error,
            latency_ms=result.latency_ms,
        )
        self.db.add(call)
        self.db.commit()
        return self._serialize_tool_call(call)

    def get(self, trace_id: str) -> dict | None:
        trace = self.db.get(TraceModel, trace_id)
        if trace is None:
            return None
        calls = self.db.execute(
            select(ToolCallModel).where(ToolCallModel.trace_id == trace_id).order_by(ToolCallModel.created_at)
        ).scalars()
        return self._serialize_trace(trace, [self._serialize_tool_call(call) for call in calls])

    def mark_finished(self, trace_id: str, status: str, final_answer: str, retrieved_docs: list, latency_ms: int) -> None:
        self.update(
            trace_id,
            status=status,
            final_answer=final_answer,
            retrieved_docs=retrieved_docs,
            latency_ms=latency_ms,
            finished_at=datetime.utcnow(),
        )

    def mark_failed(self, trace_id: str, error: str, latency_ms: int) -> None:
        self.update(
            trace_id,
            status="failed",
            error=error,
            latency_ms=latency_ms,
            finished_at=datetime.utcnow(),
        )

    def _serialize_trace(self, trace: TraceModel, tool_calls: list[dict]) -> dict:
        return {
            "id": trace.id,
            "user_id": trace.user_id,
            "conversation_id": trace.conversation_id,
            "message": trace.message,
            "intent": trace.intent,
            "route_confidence": trace.route_confidence,
            "route": trace.route or {},
            "plan": trace.plan or [],
            "retrieved_docs": trace.retrieved_docs or [],
            "tool_calls": tool_calls,
            "memory_ops": trace.memory_ops or [],
            "ingestion_ops": trace.ingestion_ops or [],
            "final_answer": trace.final_answer,
            "latency_ms": trace.latency_ms,
            "status": trace.status,
            "error": trace.error,
            "created_at": trace.created_at.isoformat() if trace.created_at else None,
            "finished_at": trace.finished_at.isoformat() if trace.finished_at else None,
        }

    def _serialize_tool_call(self, call: ToolCallModel) -> dict:
        return {
            "id": call.id,
            "trace_id": call.trace_id,
            "tool_name": call.tool_name,
            "params": call.params or {},
            "result": call.result or {},
            "success": call.success,
            "error": call.error,
            "latency_ms": call.latency_ms,
            "created_at": call.created_at.isoformat() if call.created_at else None,
        }
