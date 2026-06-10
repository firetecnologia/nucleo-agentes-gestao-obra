from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload

from .base_agent import BaseDepartmentAgent, has_any


class ProjectsAgent(BaseDepartmentAgent):
    agent_name = "ProjectsAgent"
    department = "Projetos"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        text = self.task_text(task)
        critical_terms = {"conflito", "incompleto", "sem detalhe", "rfi", "incompatibil"}
        if has_any(text, critical_terms) and baseline.risk_level in {"high", "critical"}:
            return self.from_decision(
                baseline,
                analysis="Projetos identificou conflito ou lacuna critica antes da execucao.",
                decision_override="blocked",
                requires_human_review=True,
                recommended_actions=[
                    "Bloquear execucao ate revisar compatibilizacao, versao e detalhe executivo."
                ],
            )
        return self.from_decision(
            baseline,
            analysis="Projetos nao identificou conflito critico adicional.",
        )
