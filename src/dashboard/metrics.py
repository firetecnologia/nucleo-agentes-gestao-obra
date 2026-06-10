from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable
import unicodedata

from .dashboard_models import DashboardMetrics, DecisionHistoryEntry
from .decision_history import PENDING_DECISIONS, latest_decisions_by_task


ACTIVE_RISKS = {"medium", "high", "critical"}
FINANCIAL_IMPACTS = {"medio", "media", "alto", "alta", "critico", "critica"}


def calculate_metrics(
    history: Iterable[DecisionHistoryEntry],
    *,
    analyses: Iterable[dict[str, Any]] | None = None,
    events: Iterable[dict[str, Any]] | None = None,
    reports: Iterable[dict[str, Any]] | None = None,
) -> DashboardMetrics:
    latest_entries = latest_decisions_by_task(history)
    total = len(latest_entries)

    approved_count = _count_decision(latest_entries, "approved")
    correction_count = _count_decision(latest_entries, "request_correction")
    blocked_count = _count_decision(latest_entries, "blocked")
    human_review_count = sum(1 for entry in latest_entries if entry.requires_human_review)
    medium_risk_count = _count_risk(latest_entries, "medium")
    high_risk_count = _count_risk(latest_entries, "high")
    critical_risk_count = _count_risk(latest_entries, "critical")
    client_decision_count = _count_decision(latest_entries, "ask_client")
    financial_impact_count = count_financial_impacts(
        analyses=analyses,
        events=events,
        reports=reports,
    )
    department_bottlenecks = consolidate_department_bottlenecks(
        latest_entries,
        reports=reports,
    )
    pending_or_rework_count = sum(
        1
        for entry in latest_entries
        if entry.decision in PENDING_DECISIONS or entry.requires_human_review
    )

    approval_rate = round(approved_count / total, 4) if total else 0.0
    rework_pending_rate = round(pending_or_rework_count / total, 4) if total else 0.0

    return DashboardMetrics(
        total_tasks_analyzed=total,
        approved_count=approved_count,
        correction_count=correction_count,
        blocked_count=blocked_count,
        human_review_count=human_review_count,
        medium_risk_count=medium_risk_count,
        high_risk_count=high_risk_count,
        critical_risk_count=critical_risk_count,
        client_decision_count=client_decision_count,
        financial_impact_count=financial_impact_count,
        department_bottlenecks=department_bottlenecks,
        approval_rate=approval_rate,
        rework_pending_rate=rework_pending_rate,
        health_index=calculate_health_index(
            critical_risk_count=critical_risk_count,
            high_risk_count=high_risk_count,
            blocked_count=blocked_count,
            correction_count=correction_count,
            human_review_count=human_review_count,
            client_decision_count=client_decision_count,
            financial_impact_count=financial_impact_count,
            bottleneck_count=sum(department_bottlenecks.values()),
        ),
    )


def consolidate_department_bottlenecks(
    history: Iterable[DecisionHistoryEntry],
    *,
    reports: Iterable[dict[str, Any]] | None = None,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for entry in history:
        if (
            entry.decision not in {"approved", "monitor", "create_next_tasks"}
            or entry.risk_level in ACTIVE_RISKS
            or entry.requires_human_review
        ):
            counts[entry.department or "Sem departamento"] += 1

    for report in reports or []:
        for department, count in (report.get("department_bottlenecks") or {}).items():
            department_name = str(department or "Sem departamento")
            counts[department_name] = max(counts[department_name], int(count or 0))

    return dict(counts)


def build_department_summary(
    history: Iterable[DecisionHistoryEntry],
    metrics: DashboardMetrics,
) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(_empty_department_summary)
    for entry in latest_decisions_by_task(history):
        department = entry.department or "Sem departamento"
        summary[department]["total"] += 1
        if entry.decision == "approved":
            summary[department]["approved"] += 1
        if entry.decision == "request_correction":
            summary[department]["correction"] += 1
        if entry.decision == "blocked":
            summary[department]["blocked"] += 1
        if entry.requires_human_review:
            summary[department]["human_review"] += 1
        if entry.risk_level == "high":
            summary[department]["high_risk"] += 1
        if entry.risk_level == "critical":
            summary[department]["critical_risk"] += 1

    for department, count in metrics.department_bottlenecks.items():
        summary[department]["bottlenecks"] = count

    return {department: dict(values) for department, values in summary.items()}


def count_financial_impacts(
    *,
    analyses: Iterable[dict[str, Any]] | None = None,
    events: Iterable[dict[str, Any]] | None = None,
    reports: Iterable[dict[str, Any]] | None = None,
) -> int:
    impacted_task_ids: set[str] = set()
    anonymous_impacts = 0
    report_impact_count = 0

    for item in analyses or []:
        if _has_financial_impact(item):
            task_id = str(item.get("task_id") or "")
            if task_id:
                impacted_task_ids.add(task_id)
            else:
                anonymous_impacts += 1

    for event in events or []:
        payload = event.get("task_payload") or {}
        if event.get("event_type") == "financial_impact_detected" or _has_financial_impact(payload):
            task_id = str(event.get("task_id") or payload.get("task_id") or "")
            if task_id:
                impacted_task_ids.add(task_id)
            else:
                anonymous_impacts += 1

    for report in reports or []:
        financial_impacts = list(report.get("financial_impacts") or [])
        report_impact_count = max(report_impact_count, len(financial_impacts))

    raw_impact_count = len(impacted_task_ids) + anonymous_impacts
    return max(raw_impact_count, report_impact_count)


def calculate_health_index(
    *,
    critical_risk_count: int,
    high_risk_count: int,
    blocked_count: int,
    correction_count: int,
    human_review_count: int,
    client_decision_count: int,
    financial_impact_count: int,
    bottleneck_count: int,
) -> int:
    score = 100
    score -= critical_risk_count * 25
    score -= high_risk_count * 12
    score -= blocked_count * 12
    score -= correction_count * 8
    score -= human_review_count * 5
    score -= client_decision_count * 6
    score -= financial_impact_count * 10
    score -= bottleneck_count * 3
    return max(0, min(100, score))


def _count_decision(history: Iterable[DecisionHistoryEntry], decision: str) -> int:
    return sum(1 for entry in history if entry.decision == decision)


def _count_risk(history: Iterable[DecisionHistoryEntry], risk_level: str) -> int:
    return sum(1 for entry in history if entry.risk_level == risk_level)


def _empty_department_summary() -> dict[str, int]:
    return {
        "total": 0,
        "approved": 0,
        "correction": 0,
        "blocked": 0,
        "human_review": 0,
        "high_risk": 0,
        "critical_risk": 0,
        "bottlenecks": 0,
    }


def _has_financial_impact(item: dict[str, Any]) -> bool:
    raw_value = (
        item.get("impacto_financeiro")
        or item.get("financial_impact")
        or item.get("impacto")
    )
    return _normalize(raw_value) in FINANCIAL_IMPACTS


def _normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    return "".join(char for char in text if not unicodedata.combining(char))
