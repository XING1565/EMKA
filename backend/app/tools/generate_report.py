from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import ToolResult
from backend.app.tools.base import Tool


class GenerateReportTool(Tool):
    name = "generate_report"
    description = "Generate a Markdown report"
    input_schema = {"type": "object", "properties": {"message": {"type": "string"}}}

    async def run(self, params: dict, ctx: RuntimeContext) -> ToolResult:
        message = params.get("message") or ctx.request.message
        content = (
            "# EMKA Mock Report\n\n"
            f"## 用户请求\n\n{message}\n\n"
            "## 结论\n\n"
            "Phase 1 已使用 mock RAG 证据生成结构化报告。"
        )
        report = {"title": "EMKA Mock Report", "content_md": content}
        return ToolResult(
            success=True,
            tool_name=self.name,
            data={"report": report, "answer": "已生成 EMKA Mock Report。"},
        )
