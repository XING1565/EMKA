from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from backend.app.runtime.models import RuntimeRequest


@dataclass
class RuntimeContext:
    request: RuntimeRequest
    trace_id: str
    db: Session
    memory_context: dict[str, Any] = field(default_factory=dict)
    intermediate_results: list[dict[str, Any]] = field(default_factory=list)
