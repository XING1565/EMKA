from backend.app.rag.pipeline import RAGPipeline
from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import ToolResult
from backend.app.tools.base import Tool


class SearchDocsTool(Tool):
    name = "search_docs"
    description = "Search enterprise multimodal knowledge materials"
    input_schema = {"type": "object", "properties": {"query": {"type": "string"}}}

    async def run(self, params: dict, ctx: RuntimeContext) -> ToolResult:
        if ctx.db is None:
            return ToolResult(success=True, tool_name=self.name, data={"retrieved_docs": []})
        query = params.get("query") or params.get("message") or ""
        docs = RAGPipeline(ctx.db).search(query, top_k=5)
        return ToolResult(success=True, tool_name=self.name, data={"retrieved_docs": docs})
