from time import perf_counter

from sqlalchemy.orm import Session

from backend.app.core.identity import prepare_runtime_identity
from backend.app.memory.service import MemoryService
from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import RuntimeRequest, RuntimeResponse
from backend.app.runtime.planner import TaskPlanner
from backend.app.runtime.router import IntentRouter
from backend.app.tools.registry import build_default_registry
from backend.app.trace.recorder import TraceRecorder


class RuntimeOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.router = IntentRouter()
        self.planner = TaskPlanner()
        self.tools = build_default_registry()
        self.trace = TraceRecorder(db)

    async def run(self, request: RuntimeRequest) -> RuntimeResponse:
        start = perf_counter()
        user_id, conversation_id = prepare_runtime_identity(self.db, request.user_id, request.conversation_id)
        request = request.model_copy(update={"user_id": user_id, "conversation_id": conversation_id})
        trace_id = self.trace.start_trace(request)
        ctx = RuntimeContext(request=request, trace_id=trace_id, db=self.db)
        memory_service = MemoryService(self.db)
        tool_calls: list[dict] = []
        retrieved_docs: list[dict] = []
        memory_ops: list[dict] = []
        report: dict | None = None
        answer = ""

        try:
            ctx.memory_context, memory_ops = memory_service.load_context(request.user_id, request.conversation_id)
            self.trace.record_memory_ops(trace_id, memory_ops)

            route = self.router.route(
                request.message,
                memory_context=ctx.memory_context,
                available_tools=self.tools.list_names(),
            )
            self.trace.record_router(trace_id, route)

            plan = self.planner.plan(request.message, route, self.tools.list_names())
            self.trace.record_plan(trace_id, plan)

            for step in plan.steps:
                params = dict(step.input)
                params.setdefault("message", request.message)
                params["previous_results"] = ctx.intermediate_results

                result = await self.tools.execute(step.tool, params, ctx)
                result_data = result.model_dump()
                tool_call = self.trace.record_tool_call(trace_id, step.tool, params, result)
                tool_calls.append(tool_call)
                ctx.intermediate_results.append(result_data)

                retrieved_docs.extend(result.data.get("retrieved_docs", []))
                if result.data.get("report"):
                    report = result.data["report"]
                if result.data.get("answer"):
                    answer = result.data["answer"]
                elif result.data.get("summary"):
                    answer = result.data["summary"]

            if not answer:
                answer = "No tool result was available."

            memory_ops.extend(
                memory_service.write_after_run(
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    message=request.message,
                    answer=answer,
                )
            )
            self.trace.record_memory_ops(trace_id, memory_ops)

            latency_ms = int((perf_counter() - start) * 1000)
            failed = any(not call.get("success", False) for call in tool_calls)
            self.trace.finish_trace(
                trace_id,
                final_answer=answer,
                retrieved_docs=retrieved_docs,
                latency_ms=latency_ms,
                status="failed" if failed else "success",
            )

            return RuntimeResponse(
                answer=answer,
                report=report,
                trace_id=trace_id,
                route=route.model_dump(),
                plan=[step.model_dump() for step in plan.steps],
                retrieved_docs=retrieved_docs,
                tool_calls=tool_calls,
                memory_ops=memory_ops,
                ingestion_ops=[],
            )
        except Exception as exc:
            latency_ms = int((perf_counter() - start) * 1000)
            self.trace.fail_trace(trace_id, error=str(exc), latency_ms=latency_ms)
            raise
