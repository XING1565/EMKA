from typing import Any, Literal

from pydantic import BaseModel, Field

Modality = Literal["text", "table", "image"]
Intent = Literal[
    "question",
    "summary",
    "compare",
    "generate_report",
    "search_knowledge",
    "execute_tool",
    "multimodal_analysis",
]


class RuntimeRequest(BaseModel):
    user_id: str | None = None
    conversation_id: str | None = None
    message: str
    mode: str = "auto"


class RouteDecision(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    required_modalities: list[Modality] = Field(default_factory=list)


class PlanStep(BaseModel):
    id: str
    action: str
    tool: str
    input: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class TaskPlan(BaseModel):
    steps: list[PlanStep] = Field(default_factory=list)


class ToolResult(BaseModel):
    success: bool
    tool_name: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    latency_ms: int = 0


class MultimodalIngestResult(BaseModel):
    title: str
    modality: Modality
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeResponse(BaseModel):
    answer: str
    report: dict[str, Any] | None = None
    trace_id: str
    route: dict[str, Any]
    plan: list[dict[str, Any]]
    retrieved_docs: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    memory_ops: list[dict[str, Any]] = Field(default_factory=list)
    ingestion_ops: list[dict[str, Any]] = Field(default_factory=list)
