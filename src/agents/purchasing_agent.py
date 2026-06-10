from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload

from .base_agent import BaseDepartmentAgent, has_any, normalize_text


class PurchasingAgent(BaseDepartmentAgent):
    agent_name = "PurchasingAgent"
    department = "Compras"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        text = self.task_text(task)
        missing = {normalize_text(item) for item in baseline.missing_evidence}
        if task.precisa_aprovacao_gestao or missing.intersection(
            {"orcamento", "cotacao", "especificacao"}
        ):
            return self.from_decision(
                baseline,
                analysis="Compras identificou falta de especificacao/cotacao ou aprovacao necessaria.",
                decision_override="blocked",
                requires_human_review=True,
                recommended_actions=[
                    "Bloquear compra ate validar especificacao, quantidade, cotacao e aprovacao interna."
                ],
            )
        if has_any(text, {"fornecedor", "prazo de entrega", "sem estoque"}):
            return self.from_decision(
                baseline,
                analysis="Compras identificou risco operacional de fornecedor ou prazo.",
                decision_override="monitor",
                recommended_actions=["Monitorar fornecedor e prazo de entrega antes da proxima etapa."],
            )
        return self.from_decision(
            baseline,
            analysis="Compras nao identificou bloqueio adicional.",
        )
