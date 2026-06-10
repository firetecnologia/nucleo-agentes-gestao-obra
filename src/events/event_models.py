from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


EventType = Literal[
    "task_ready_for_agent_review",
    "task_overdue",
    "new_attachment_added",
    "client_decision_required",
    "financial_impact_detected",
]

KNOWN_EVENT_TYPES: set[str] = {
    "task_ready_for_agent_review",
    "task_overdue",
    "new_attachment_added",
    "client_decision_required",
    "financial_impact_detected",
}


@dataclass(slots=True)
class AsanaEvent:
    event_type: str
    task_id: str
    event_id: str | None = None
    occurred_at: str | None = None
    source: str = "asana_simulado"
    dry_run: bool = True
    task_payload: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AsanaEvent":
        task_id = data.get("task_id") or data.get("task_gid") or ""
        return cls(
            event_type=str(data.get("event_type", "")),
            task_id=str(task_id),
            event_id=data.get("event_id"),
            occurred_at=data.get("occurred_at"),
            source=str(data.get("source", "asana_simulado")),
            dry_run=bool(data.get("dry_run", True)),
            task_payload=data.get("task_payload"),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(slots=True)
class EventProcessingResult:
    event_type: str
    processed: bool
    dry_run: bool
    decision: str | None = None
    risk_level: str | None = None
    specialist_agent: str | None = None
    specialist_analysis: dict[str, Any] | None = None
    planned_operations: list[dict[str, Any]] = field(default_factory=list)
    log_entry: dict[str, Any] = field(default_factory=dict)
    requires_human_review: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {
            "event_type": self.event_type,
            "processed": self.processed,
            "dry_run": self.dry_run,
            "decision": self.decision,
            "planned_operations": self.planned_operations,
            "log_entry": self.log_entry,
        }
        if self.risk_level is not None:
            output["risk_level"] = self.risk_level
        if self.specialist_agent is not None:
            output["specialist_agent"] = self.specialist_agent
        if self.specialist_analysis is not None:
            output["specialist_analysis"] = self.specialist_analysis
        if self.requires_human_review:
            output["requires_human_review"] = self.requires_human_review
        if self.error:
            output["error"] = self.error
        return output
