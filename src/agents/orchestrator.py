from __future__ import annotations

from src.domain.decision_engine import decide
from src.domain.models import AgentDecision, Decision, NextTask, RiskLevel, TaskPayload

from .base_agent import BaseDepartmentAgent, SpecialistAnalysis, normalize_text
from .client_service_agent import ClientServiceAgent
from .engineering_agent import EngineeringAgent
from .finance_agent import FinanceAgent
from .planning_agent import PlanningAgent
from .projects_agent import ProjectsAgent
from .purchasing_agent import PurchasingAgent
from .quality_agent import QualityAgent


DECISION_PRIORITY: dict[Decision, int] = {
    "approved": 0,
    "create_next_tasks": 1,
    "monitor": 2,
    "request_correction": 3,
    "ask_client": 4,
    "escalate_management": 5,
    "blocked": 6,
}

RISK_PRIORITY: dict[RiskLevel, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

SPECIALIST_FACTORIES: dict[str, type[BaseDepartmentAgent]] = {
    "planejamento": PlanningAgent,
    "cronograma": PlanningAgent,
    "projetos": ProjectsAgent,
    "projeto": ProjectsAgent,
    "engenharia": EngineeringAgent,
    "campo": EngineeringAgent,
    "obra": EngineeringAgent,
    "compras": PurchasingAgent,
    "compra": PurchasingAgent,
    "suprimentos": PurchasingAgent,
    "financeiro": FinanceAgent,
    "financeira": FinanceAgent,
    "atendimento": ClientServiceAgent,
    "cliente": ClientServiceAgent,
    "qualidade": QualityAgent,
}


class OrchestratorAgent:
    """Agente orquestrador da gestao premium de obras."""

    def analyze(self, task: TaskPayload) -> AgentDecision:
        general_decision = decide(task)
        specialist = self._select_specialist(task)

        if specialist is None:
            return general_decision

        specialist_analysis = specialist.analyze(task)
        return self._combine_decisions(general_decision, specialist_analysis)

    def _select_specialist(self, task: TaskPayload) -> BaseDepartmentAgent | None:
        department = normalize_text(task.departamento_responsavel)
        for alias, agent_factory in SPECIALIST_FACTORIES.items():
            if alias in department:
                return agent_factory()
        return None

    def _combine_decisions(
        self,
        general_decision: AgentDecision,
        specialist_analysis: SpecialistAnalysis,
    ) -> AgentDecision:
        final_decision = self._most_conservative_decision(
            general_decision.decision,
            specialist_analysis.decision,
        )
        final_risk = self._highest_risk(general_decision.risk_level, specialist_analysis.risk_level)
        requires_human_review = (
            general_decision.requires_human_review
            or specialist_analysis.requires_human_review
            or final_decision in {"blocked", "escalate_management", "ask_client", "request_correction"}
        )
        next_tasks = self._allowed_next_tasks(
            final_decision,
            self._dedupe_next_tasks(general_decision.next_tasks + specialist_analysis.next_tasks),
        )
        recommended_actions = self._dedupe_strings(
            general_decision.recommended_actions + specialist_analysis.recommended_actions
        )
        missing_evidence = self._dedupe_strings(
            general_decision.missing_evidence + specialist_analysis.missing_evidence
        )
        validated_evidence = self._dedupe_strings(
            general_decision.validated_evidence + specialist_analysis.validated_evidence
        )

        analysis = (
            f"{general_decision.analysis} "
            f"Analise especialista ({specialist_analysis.agent_name}): {specialist_analysis.analysis}"
        )
        asana_comment = (
            f"{general_decision.asana_comment} "
            f"Agente especialista: {specialist_analysis.agent_name}. "
            f"Decisao final conservadora: {final_decision}. "
            "Todas as acoes permanecem em dry-run e exigem revisao humana quando indicado."
        )

        return AgentDecision(
            decision=final_decision,
            risk_level=final_risk,
            analysis=analysis,
            asana_comment=asana_comment,
            validated_evidence=validated_evidence,
            missing_evidence=missing_evidence,
            recommended_actions=recommended_actions,
            next_tasks=next_tasks,
            requires_human_review=requires_human_review,
            specialist_agent=specialist_analysis.agent_name,
            specialist_analysis=specialist_analysis.to_dict(),
        )

    def _most_conservative_decision(self, first: Decision, second: Decision) -> Decision:
        return first if DECISION_PRIORITY[first] >= DECISION_PRIORITY[second] else second

    def _highest_risk(self, first: RiskLevel, second: RiskLevel) -> RiskLevel:
        return first if RISK_PRIORITY[first] >= RISK_PRIORITY[second] else second

    def _allowed_next_tasks(self, decision: Decision, next_tasks: list[NextTask]) -> list[NextTask]:
        if decision in {"create_next_tasks", "ask_client"}:
            return next_tasks
        return []

    def _dedupe_strings(self, values: list[str]) -> list[str]:
        deduped: list[str] = []
        for value in values:
            if value not in deduped:
                deduped.append(value)
        return deduped

    def _dedupe_next_tasks(self, next_tasks: list[NextTask]) -> list[NextTask]:
        deduped: list[NextTask] = []
        seen: set[tuple[str, str]] = set()
        for task in next_tasks:
            key = (task.name, task.department)
            if key not in seen:
                deduped.append(task)
                seen.add(key)
        return deduped
