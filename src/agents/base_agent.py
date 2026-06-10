from __future__ import annotations

import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Any

from src.domain.decision_engine import decide
from src.domain.models import AgentDecision, Decision, NextTask, RiskLevel, TaskPayload


@dataclass(slots=True)
class SpecialistAnalysis:
    agent_name: str
    department: str
    decision: Decision
    risk_level: RiskLevel
    analysis: str
    validated_evidence: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    next_tasks: list[NextTask] = field(default_factory=list)
    requires_human_review: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "department": self.department,
            "decision": self.decision,
            "risk_level": self.risk_level,
            "analysis": self.analysis,
            "validated_evidence": self.validated_evidence,
            "missing_evidence": self.missing_evidence,
            "recommended_actions": self.recommended_actions,
            "next_tasks": [asdict(task) for task in self.next_tasks],
            "requires_human_review": self.requires_human_review,
        }


class BaseDepartmentAgent:
    agent_name = "BaseDepartmentAgent"
    department = "Geral"

    def analyze(self, task: TaskPayload) -> SpecialistAnalysis:
        baseline = decide(task)
        return self.from_decision(
            baseline,
            analysis=f"{self.department}: analise especialista sem regra adicional critica.",
        )

    def from_decision(
        self,
        decision: AgentDecision,
        *,
        analysis: str,
        decision_override: Decision | None = None,
        risk_override: RiskLevel | None = None,
        recommended_actions: list[str] | None = None,
        requires_human_review: bool | None = None,
        next_tasks: list[NextTask] | None = None,
    ) -> SpecialistAnalysis:
        return SpecialistAnalysis(
            agent_name=self.agent_name,
            department=self.department,
            decision=decision_override or decision.decision,
            risk_level=risk_override or decision.risk_level,
            analysis=analysis,
            validated_evidence=list(decision.validated_evidence),
            missing_evidence=list(decision.missing_evidence),
            recommended_actions=list(recommended_actions or decision.recommended_actions),
            next_tasks=list(next_tasks if next_tasks is not None else decision.next_tasks),
            requires_human_review=decision.requires_human_review
            if requires_human_review is None
            else requires_human_review,
        )

    def task_text(self, task: TaskPayload) -> str:
        parts = [
            task.task_name,
            task.etapa_obra,
            task.status_agente,
            task.description or "",
            " ".join(comment.text for comment in task.comments),
            " ".join(str(value) for value in task.custom_notes.values()),
        ]
        return normalize_text(" ".join(parts))


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", value.lower().strip())
    return "".join(char for char in text if not unicodedata.combining(char))


def has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)
