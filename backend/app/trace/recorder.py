from sqlalchemy.orm import Session

from backend.app.runtime.models import RouteDecision, RuntimeRequest, TaskPlan, ToolResult
from backend.app.trace.repository import TraceRepository


class TraceRecorder:
    def __init__(self, db: Session):
        self.repository = TraceRepository(db)

    def start_trace(self, request: RuntimeRequest) -> str:
        return self.repository.create(request)

    def record_router(self, trace_id: str, route: RouteDecision) -> None:
        self.repository.update(
            trace_id,
            intent=route.intent,
            route_confidence=route.confidence,
            route=route.model_dump(),
        )

    def record_plan(self, trace_id: str, plan: TaskPlan) -> None:
        self.repository.update(trace_id, plan=[step.model_dump() for step in plan.steps])

    def record_memory_ops(self, trace_id: str, memory_ops: list[dict]) -> None:
        self.repository.update(trace_id, memory_ops=memory_ops)

    def record_tool_call(self, trace_id: str, tool_name: str, params: dict, result: ToolResult) -> dict:
        return self.repository.add_tool_call(trace_id, tool_name, params, result)

    def finish_trace(
        self,
        trace_id: str,
        final_answer: str,
        retrieved_docs: list,
        latency_ms: int,
        status: str = "success",
    ) -> None:
        self.repository.mark_finished(trace_id, status, final_answer, retrieved_docs, latency_ms)

    def fail_trace(self, trace_id: str, error: str, latency_ms: int) -> None:
        self.repository.mark_failed(trace_id, error, latency_ms)
