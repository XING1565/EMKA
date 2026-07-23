from __future__ import annotations

from time import perf_counter

from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import ToolResult
from backend.app.tools.base import Tool
from backend.app.tools.generate_report import GenerateReportTool
from backend.app.tools.read_doc import ReadDocTool
from backend.app.tools.search_docs import SearchDocsTool
from backend.app.tools.summarize import SummarizeTool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self._tools.values()
        ]

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    async def execute(self, tool_name: str, params: dict, ctx: RuntimeContext) -> ToolResult:
        started = perf_counter()
        tool = self._tools.get(tool_name)
        if tool is None:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=f"tool not found: {tool_name}",
                latency_ms=int((perf_counter() - started) * 1000),
            )
        try:
            result = await tool.run(params, ctx)
            result.latency_ms = int((perf_counter() - started) * 1000)
            return result
        except Exception as exc:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=str(exc),
                latency_ms=int((perf_counter() - started) * 1000),
            )


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(SearchDocsTool())
    registry.register(ReadDocTool())
    registry.register(SummarizeTool())
    registry.register(GenerateReportTool())
    return registry
