from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import AgentDecision, TaskPayload


class OrchestratorAgent:
    """Agente orquestrador da gestão premium de obras."""

    def analyze(self, task: TaskPayload) -> AgentDecision:
        return decide(task)
