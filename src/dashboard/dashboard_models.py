from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


WorkHealthStatus = Literal["on_track", "attention", "at_risk", "critical"]


@dataclass(slots=True)
class DashboardPeriod:
    inicio: str | None = None
    fim: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "DashboardPeriod":
        payload = data or {}
        return cls(
            inicio=payload.get("inicio"),
            fim=payload.get("fim"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DashboardInput:
    obra: str
    cliente: str
    periodo: DashboardPeriod
    analyses: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    reports: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DashboardInput":
        return cls(
            obra=str(data.get("obra", "")),
            cliente=str(data.get("cliente", "")),
            periodo=DashboardPeriod.from_dict(data.get("periodo") or data.get("period")),
            analyses=list(data.get("analyses") or []),
            events=list(data.get("events") or []),
            reports=list(data.get("reports") or []),
        )


@dataclass(slots=True)
class DecisionHistoryEntry:
    task_id: str
    task_name: str
    department: str
    decision: str
    risk_level: str
    specialist_agent: str | None
    requires_human_review: bool
    source: str
    created_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DashboardMetrics:
    total_tasks_analyzed: int = 0
    approved_count: int = 0
    correction_count: int = 0
    blocked_count: int = 0
    human_review_count: int = 0
    medium_risk_count: int = 0
    high_risk_count: int = 0
    critical_risk_count: int = 0
    client_decision_count: int = 0
    financial_impact_count: int = 0
    department_bottlenecks: dict[str, int] = field(default_factory=dict)
    approval_rate: float = 0.0
    rework_pending_rate: float = 0.0
    health_index: int = 100

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DashboardOutput:
    obra: str
    cliente: str
    health_status: WorkHealthStatus
    metrics: DashboardMetrics
    decision_history: list[DecisionHistoryEntry]
    active_risks: list[dict[str, Any]]
    pending_decisions: list[dict[str, Any]]
    department_summary: dict[str, dict[str, int]]
    recommended_management_actions: list[str]
    period: dict[str, Any]
    dry_run: bool = True
    external_operations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "obra": self.obra,
            "cliente": self.cliente,
            "health_status": self.health_status,
            "metrics": self.metrics.to_dict(),
            "decision_history": [entry.to_dict() for entry in self.decision_history],
            "active_risks": self.active_risks,
            "pending_decisions": self.pending_decisions,
            "department_summary": self.department_summary,
            "recommended_management_actions": self.recommended_management_actions,
            "period": self.period,
            "dry_run": True,
            "external_operations": [],
        }
