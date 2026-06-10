from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload

from .base_agent import BaseDepartmentAgent, normalize_text


class FinanceAgent(BaseDepartmentAgent):
    agent_name = "FinanceAgent"
    department = "Financeiro"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        impact = normalize_text(task.impacto_financeiro)
        if impact in {"medio", "media", "alto", "alta", "critico", "critica"}:
            return self.from_decision(
                baseline,
                analysis="Financeiro identificou impacto financeiro que exige revisao humana.",
                decision_override="escalate_management",
                requires_human_review=True,
                recommended_actions=[
                    "Gestao/Financeiro devem revisar previsto x realizado, medicao e vinculo com a obra."
                ],
            )
        return self.from_decision(
            baseline,
            analysis="Financeiro nao identificou desvio financeiro relevante.",
        )
