from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload

from .base_agent import BaseDepartmentAgent, normalize_text


class QualityAgent(BaseDepartmentAgent):
    agent_name = "QualityAgent"
    department = "Qualidade"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        missing = {normalize_text(item) for item in baseline.missing_evidence}
        if "checklist" in missing or (not task.evidencia_obrigatoria and not task.attachments):
            return self.from_decision(
                baseline,
                analysis="Qualidade impediu aprovacao por falta de checklist ou evidencia minima.",
                decision_override="request_correction",
                requires_human_review=True,
                recommended_actions=[
                    "Anexar checklist/evidencia minima antes de liberar a etapa."
                ],
            )
        return self.from_decision(
            baseline,
            analysis="Qualidade encontrou evidencia suficiente para analise inicial.",
        )
