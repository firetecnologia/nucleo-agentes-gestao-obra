from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import NextTask, TaskPayload

from .base_agent import BaseDepartmentAgent


class ClientServiceAgent(BaseDepartmentAgent):
    agent_name = "ClientServiceAgent"
    department = "Atendimento"

    def analyze(self, task: TaskPayload):
        baseline = decide(task)
        if task.precisa_aprovacao_cliente or baseline.decision == "ask_client":
            next_tasks = list(baseline.next_tasks)
            if not next_tasks:
                next_tasks.append(
                    NextTask(
                        name=f"Preparar rascunho para cliente - {task.task_name}",
                        department="Atendimento",
                        description="Preparar rascunho interno para revisao humana. Nao enviar automaticamente.",
                        suggested_owner="Atendimento",
                        suggested_due="24h",
                    )
                )
            return self.from_decision(
                baseline,
                analysis="Atendimento identificou decisao/comunicacao de cliente que exige revisao humana.",
                decision_override="ask_client",
                requires_human_review=True,
                recommended_actions=[
                    "Preparar rascunho interno para revisao humana. Nenhuma mensagem deve ser enviada automaticamente."
                ],
                next_tasks=next_tasks,
            )
        return self.from_decision(
            baseline,
            analysis="Atendimento nao identificou necessidade adicional de comunicacao com cliente.",
        )
