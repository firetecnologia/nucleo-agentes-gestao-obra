from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable
import unicodedata

from .client_report_draft import build_client_report_draft
from .internal_daily_report import build_internal_daily_report
from .report_models import HealthStatus, ReportInput, ReportItem, ReportOutput, ReportType
from .weekly_management_report import build_weekly_management_report


RISK_PRIORITY = {"low": 0, "medium": 1, "high": 2, "critical": 3}
PENDING_DECISIONS = {"blocked", "escalate_management", "ask_client", "request_correction"}


def build_report_from_dict(data: dict, report_type: ReportType) -> ReportOutput:
    return build_report(ReportInput.from_dict(data), report_type)


def build_report(report_input: ReportInput, report_type: ReportType) -> ReportOutput:
    if report_type == "internal_daily":
        return build_internal_daily_report(report_input)
    if report_type == "weekly_management":
        return build_weekly_management_report(report_input)
    if report_type == "client_draft":
        return build_client_report_draft(report_input)
    raise ValueError(f"Tipo de relatorio nao suportado: {report_type}")


def classify_health_status(items: list[ReportItem]) -> HealthStatus:
    if any(item.risk_level == "critical" or item.decision == "blocked" for item in items):
        return "critical"

    high_risks = [item for item in items if item.risk_level == "high"]
    high_financial = [
        item for item in items if _normalize(item.impacto_financeiro) in {"alto", "alta", "critico", "critica"}
    ]
    critical_deadline = [
        item for item in items if _normalize(item.impacto_prazo) in {"critico", "critica"}
    ]
    if len(high_risks) >= 2 or high_financial or critical_deadline:
        return "at_risk"

    attention_items = [
        item
        for item in items
        if item.risk_level == "medium"
        or item.decision in {"request_correction", "ask_client", "escalate_management"}
        or item.requires_human_review
    ]
    bottlenecks = consolidate_department_bottlenecks(items)
    if attention_items or any(count > 1 for count in bottlenecks.values()):
        return "attention"

    return "on_track"


def summarize_tasks(items: list[ReportItem]) -> list[dict[str, str]]:
    return [
        {
            "task_id": item.task_id,
            "task_name": item.task_name,
            "department": item.department,
            "decision": item.decision,
            "risk_level": item.risk_level,
        }
        for item in items
    ]


def consolidate_department_bottlenecks(items: Iterable[ReportItem]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in items:
        if item.decision != "approved" or item.risk_level in {"medium", "high", "critical"}:
            department = item.department or "Sem departamento"
            counts[department] += 1
    return dict(counts)


def consolidate_department_pending(items: Iterable[ReportItem]) -> dict[str, list[str]]:
    pending: dict[str, list[str]] = defaultdict(list)
    for item in items:
        if item.decision in PENDING_DECISIONS or item.missing_evidence:
            department = item.department or "Sem departamento"
            pending[department].append(item.short_label())
    return dict(pending)


def list_pending_decisions(items: Iterable[ReportItem]) -> list[str]:
    decisions: list[str] = []
    for item in items:
        if item.requires_human_review or item.decision in PENDING_DECISIONS:
            decisions.append(f"{item.short_label()}: {item.decision}")
    return _dedupe(decisions)


def list_active_risks(items: Iterable[ReportItem]) -> list[str]:
    risks: list[str] = []
    for item in items:
        if item.risk_level in {"medium", "high", "critical"}:
            risks.append(f"{item.short_label()}: risco {item.risk_level}")
        if item.decision == "blocked":
            risks.append(f"{item.short_label()}: bloqueio ativo")
    return _dedupe(risks)


def list_recommended_actions(items: Iterable[ReportItem]) -> list[str]:
    actions: list[str] = []
    for item in items:
        actions.extend(item.recommended_actions)
        if item.missing_evidence:
            actions.append(f"Completar evidencias de {item.short_label()}: {', '.join(item.missing_evidence)}")
    return _dedupe(actions)


def list_deadline_impacts(items: Iterable[ReportItem]) -> list[str]:
    impacts: list[str] = []
    for item in items:
        if _normalize(item.impacto_prazo) in {"medio", "media", "alto", "alta", "critico", "critica"}:
            impacts.append(f"{item.short_label()}: impacto de prazo {item.impacto_prazo}")
    return _dedupe(impacts)


def list_financial_impacts(items: Iterable[ReportItem]) -> list[str]:
    impacts: list[str] = []
    for item in items:
        if _normalize(item.impacto_financeiro) in {"medio", "media", "alto", "alta", "critico", "critica"}:
            impacts.append(f"{item.short_label()}: impacto financeiro {item.impacto_financeiro}")
    return _dedupe(impacts)


def build_summary(obra: str, health_status: HealthStatus, items: list[ReportItem]) -> str:
    total = len(items)
    approved = len([item for item in items if item.decision == "approved"])
    return (
        f"Obra {obra}: {total} tarefa(s) analisada(s), {approved} aprovada(s), "
        f"status geral {health_status}."
    )


def _normalize(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", (value or "").lower().strip())
    return "".join(char for char in text if not unicodedata.combining(char))


def _dedupe(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value and value not in deduped:
            deduped.append(value)
    return deduped
