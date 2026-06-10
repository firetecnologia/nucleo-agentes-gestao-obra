from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


ReportType = Literal["internal_daily", "weekly_management", "client_draft"]
HealthStatus = Literal["on_track", "attention", "at_risk", "critical"]


@dataclass(slots=True)
class ReportPeriod:
    inicio: str | None = None
    fim: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "ReportPeriod":
        payload = data or {}
        return cls(
            inicio=payload.get("inicio"),
            fim=payload.get("fim"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportItem:
    task_id: str
    task_name: str
    department: str
    decision: str
    risk_level: str
    requires_human_review: bool = False
    specialist_agent: str | None = None
    recommended_actions: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    planned_operations: list[dict[str, Any]] = field(default_factory=list)
    impacto_prazo: str | None = None
    impacto_financeiro: str | None = None
    impacto_cliente: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportItem":
        return cls(
            task_id=str(data.get("task_id", "")),
            task_name=str(data.get("task_name") or data.get("name") or ""),
            department=str(data.get("department") or data.get("departamento_responsavel") or ""),
            decision=str(data.get("decision", "")),
            risk_level=str(data.get("risk_level", "low")),
            requires_human_review=bool(data.get("requires_human_review", False)),
            specialist_agent=data.get("specialist_agent"),
            recommended_actions=list(data.get("recommended_actions") or []),
            missing_evidence=list(data.get("missing_evidence") or []),
            planned_operations=list(data.get("planned_operations") or []),
            impacto_prazo=data.get("impacto_prazo"),
            impacto_financeiro=data.get("impacto_financeiro"),
            impacto_cliente=data.get("impacto_cliente"),
        )

    def short_label(self) -> str:
        if self.task_name:
            return f"{self.task_name} ({self.department or 'Sem departamento'})"
        return f"Tarefa {self.task_id} ({self.department or 'Sem departamento'})"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportInput:
    obra: str
    periodo: ReportPeriod
    items: list[ReportItem] = field(default_factory=list)
    data_referencia: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReportInput":
        period_data = data.get("periodo") or {}
        return cls(
            obra=str(data.get("obra", "")),
            periodo=ReportPeriod.from_dict(period_data),
            items=[ReportItem.from_dict(item) for item in data.get("items") or []],
            data_referencia=data.get("data_referencia") or period_data.get("fim"),
        )


@dataclass(slots=True)
class ClientDraft:
    summary: str
    next_steps: list[str]
    pending_client_decisions: list[str]
    communicable_risks: list[str]
    control_phrase: str
    body: str
    requires_human_review: bool = True
    external_delivery: str = "draft_only_no_external_send"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportOutput:
    report_type: ReportType
    obra: str
    health_status: HealthStatus
    summary: str
    period: dict[str, Any]
    highlights: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    pending_decisions: list[str] = field(default_factory=list)
    department_bottlenecks: dict[str, int] = field(default_factory=dict)
    recommended_actions: list[str] = field(default_factory=list)
    client_draft: ClientDraft | None = None
    requires_human_review: bool = True
    dry_run: bool = True
    external_operations: list[dict[str, Any]] = field(default_factory=list)
    tasks_analyzed: list[dict[str, Any]] = field(default_factory=list)
    approved_tasks: list[str] = field(default_factory=list)
    correction_requested_tasks: list[str] = field(default_factory=list)
    blocked_tasks: list[str] = field(default_factory=list)
    active_risks: list[str] = field(default_factory=list)
    department_pending: dict[str, list[str]] = field(default_factory=dict)
    next_actions: list[str] = field(default_factory=list)
    management_decisions: list[str] = field(default_factory=list)
    deadline_impacts: list[str] = field(default_factory=list)
    financial_impacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        output = asdict(self)
        output["client_draft"] = self.client_draft.to_dict() if self.client_draft else None
        return output
