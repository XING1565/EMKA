from abc import ABC, abstractmethod

from backend.app.runtime.context import RuntimeContext
from backend.app.runtime.models import ToolResult


class Tool(ABC):
    name: str
    description: str
    input_schema: dict

    @abstractmethod
    async def run(self, params: dict, ctx: RuntimeContext) -> ToolResult:
        raise NotImplementedError
