from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload

from .base_agent import BaseDepartmentAgent, normalize_text


class EngineeringAgent(BaseDepartmentAgent):
    agent_name = "EngineeringAgent"
    department = "Engenharia"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        missing = {normalize_text(item) for item in baseline.missing_evidence}
        field_evidence = {"foto", "diario de obra", "vistoria"}
        if missing.intersection(field_evidence):
            return self.from_decision(
                baseline,
                analysis="Engenharia/Campo encontrou falta de evidencia minima de campo.",
                decision_override="request_correction",
                requires_human_review=True,
                recommended_actions=[
                    "Responsavel deve anexar foto, diario de obra ou evidencia de vistoria antes da liberacao."
                ],
            )
        return self.from_decision(
            baseline,
            analysis="Engenharia/Campo nao identificou pendencia adicional de campo.",
        )
