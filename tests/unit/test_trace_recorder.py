from backend.app.core.database import SessionLocal, init_database
from backend.app.runtime.models import RuntimeRequest, ToolResult
from backend.app.trace.recorder import TraceRecorder
from backend.app.trace.repository import TraceRepository


def test_trace_recorder_records_tool_call_and_finish():
    init_database()
    db = SessionLocal()
    try:
        recorder = TraceRecorder(db)
        trace_id = recorder.start_trace(RuntimeRequest(message="hello"))
        recorder.record_tool_call(
            trace_id,
            "search_docs",
            {"query": "hello"},
            ToolResult(success=True, tool_name="search_docs", data={"retrieved_docs": []}),
        )
        recorder.finish_trace(trace_id, "done", [], 12)

        trace = TraceRepository(db).get(trace_id)

        assert trace["status"] == "success"
        assert trace["tool_calls"][0]["tool_name"] == "search_docs"
        assert trace["latency_ms"] == 12
    finally:
        db.close()
