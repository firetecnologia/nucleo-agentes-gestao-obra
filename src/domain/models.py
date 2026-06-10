from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Decision = Literal[
    "approved",
    "request_correction",
    "escalate_management",
    "ask_client",
    "create_next_tasks",
    "blocked",
    "monitor",
]

RiskLevel = Literal["low", "medium", "high", "critical"]


@dataclass(slots=True)
class Attachment:
    name: str
    type: str | None = None


@dataclass(slots=True)
class TaskComment:
    author: str
    text: str


@dataclass(slots=True)
class NextTask:
    name: str
    department: str
    description: str
    suggested_owner: str | None = None
    suggested_due: str | None = None


@dataclass(slots=True)
class TaskPayload:
    task_id: str
    task_name: str
    obra: str
    departamento_responsavel: str
    etapa_obra: str
    status_agente: str
    prioridade: str | None = None
    assignee: str | None = None
    due_on: str | None = None
    impacto_prazo: str | None = None
    impacto_financeiro: str | None = None
    impacto_cliente: str | None = None
    proximo_departamento: str | None = None
    precisa_aprovacao_gestao: bool = False
    precisa_aprovacao_cliente: bool = False
    evidencia_obrigatoria: list[str] = field(default_factory=list)
    attachments: list[Attachment] = field(default_factory=list)
    comments: list[TaskComment] = field(default_factory=list)
    description: str | None = None
    dependencies: list[Any] = field(default_factory=list)
    custom_notes: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskPayload":
        return cls(
            task_id=str(data.get("task_id", "")),
            task_name=str(data.get("task_name", "")),
            obra=str(data.get("obra", "")),
            departamento_responsavel=str(data.get("departamento_responsavel", "")),
            etapa_obra=str(data.get("etapa_obra", "")),
            status_agente=str(data.get("status_agente", "")),
            prioridade=data.get("prioridade"),
            assignee=data.get("assignee"),
            due_on=data.get("due_on"),
            impacto_prazo=data.get("impacto_prazo"),
            impacto_financeiro=data.get("impacto_financeiro"),
            impacto_cliente=data.get("impacto_cliente"),
            proximo_departamento=data.get("proximo_departamento"),
            precisa_aprovacao_gestao=bool(data.get("precisa_aprovacao_gestao", False)),
            precisa_aprovacao_cliente=bool(data.get("precisa_aprovacao_cliente", False)),
            evidencia_obrigatoria=list(data.get("evidencia_obrigatoria", [])),
            attachments=[Attachment(**item) for item in data.get("attachments", [])],
            comments=[TaskComment(**item) for item in data.get("comments", [])],
            description=data.get("description"),
            dependencies=list(data.get("dependencies", [])),
            custom_notes=dict(data.get("custom_notes", {})),
        )


@dataclass(slots=True)
class AgentDecision:
    decision: Decision
    risk_level: RiskLevel
    analysis: str
    asana_comment: str
    validated_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    next_tasks: list[NextTask] = field(default_factory=list)
    requires_human_review: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "risk_level": self.risk_level,
            "analysis": self.analysis,
            "asana_comment": self.asana_comment,
            "validated_evidence": self.validated_evidence,
            "missing_evidence": self.missing_evidence,
            "recommended_actions": self.recommended_actions,
            "next_tasks": [asdict(task) for task in self.next_tasks],
            "requires_human_review": self.requires_human_review,
        }
