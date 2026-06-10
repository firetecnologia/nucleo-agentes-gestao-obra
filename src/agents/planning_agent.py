from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload

from .base_agent import BaseDepartmentAgent, normalize_text


class PlanningAgent(BaseDepartmentAgent):
    agent_name = "PlanningAgent"
    department = "Planejamento"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        prazo = normalize_text(task.impacto_prazo)
        if prazo in {"alto", "critico", "critica"}:
            return self.from_decision(
                baseline,
                analysis="Planejamento identificou impacto relevante no cronograma/caminho critico.",
                decision_override="escalate_management",
                requires_human_review=True,
                recommended_actions=[
                    "Gestao e Planejamento devem revisar impacto no cronograma antes de avancar."
                ],
            )
        if task.dependencies:
            return self.from_decision(
                baseline,
                analysis="Planejamento encontrou dependencias que impedem sequencia segura.",
                decision_override="blocked",
                requires_human_review=True,
                recommended_actions=["Remover dependencias antes de liberar a proxima etapa."],
            )
        return self.from_decision(
            baseline,
            analysis="Planejamento nao identificou bloqueio adicional de cronograma.",
        )
