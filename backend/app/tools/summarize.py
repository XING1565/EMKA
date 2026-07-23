from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import ToolResult
from backend.app.tools.base import Tool


class SummarizeTool(Tool):
    name = "summarize"
    description = "Summarize retrieved evidence"
    input_schema = {"type": "object", "properties": {"message": {"type": "string"}}}

    async def run(self, params: dict, ctx: RuntimeContext) -> ToolResult:
        message = params.get("message") or ctx.request.message
        previous = params.get("previous_results") or []
        evidence_count = 0
        for item in previous:
            evidence_count += len((item.get("data") or {}).get("retrieved_docs", []))
        summary = f"已基于 {evidence_count} 条模拟证据处理请求：{message}"
        return ToolResult(success=True, tool_name=self.name, data={"summary": summary})
