from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import ToolResult
from backend.app.tools.base import Tool


class ReadDocTool(Tool):
    name = "read_doc"
    description = "Read a document by id"
    input_schema = {"type": "object", "properties": {"document_id": {"type": "string"}}}

    async def run(self, params: dict, ctx: RuntimeContext) -> ToolResult:
        document_id = params.get("document_id") or "mock-doc-001"
        return ToolResult(
            success=True,
            tool_name=self.name,
            data={
                "document": {
                    "document_id": document_id,
                    "title": "项目风险周报样例",
                    "content": "这是 Phase 1 mock 文档内容，用于验证 Runtime 工具链。",
                }
            },
        )
