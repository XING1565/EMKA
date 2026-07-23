import asyncio

from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import RuntimeRequest, ToolResult
from backend.app.tools.base import Tool
from backend.app.tools.registry import ToolRegistry, build_default_registry


class BrokenTool(Tool):
    name = "broken"
    description = "broken"
    input_schema = {}

    async def run(self, params: dict, ctx: RuntimeContext) -> ToolResult:
        raise RuntimeError("boom")


def test_default_registry_executes_search_without_db_as_empty_result():
    registry = build_default_registry()
    ctx = RuntimeContext(RuntimeRequest(message="查找项目风险"), trace_id="t1", db=None)

    result = asyncio.run(registry.execute("search_docs", {"query": "项目风险"}, ctx))

    assert result.success is True
    assert result.data["retrieved_docs"] == []


def test_registry_catches_tool_errors():
    registry = ToolRegistry()
    registry.register(BrokenTool())
    ctx = RuntimeContext(RuntimeRequest(message="x"), trace_id="t1", db=None)

    result = asyncio.run(registry.execute("broken", {}, ctx))

    assert result.success is False
    assert result.error == "boom"
