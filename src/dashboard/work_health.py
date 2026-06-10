from __future__ import annotations

from typing import Iterable

from .dashboard_models import DashboardMetrics, DecisionHistoryEntry, WorkHealthStatus


def calculate_work_health(
    metrics: DashboardMetrics,
    history: Iterable[DecisionHistoryEntry] | None = None,
) -> WorkHealthStatus:
    entries = list(history or [])

    if metrics.total_tasks_analyzed == 0:
        return "attention"

    has_relevant_block = any(
        entry.decision == "blocked" and entry.risk_level in {"high", "critical"}
        for entry in entries
    )
    if metrics.critical_risk_count > 0 or has_relevant_block or metrics.blocked_count >= 2:
        return "critical"

    recurring_bottleneck = any(count >= 2 for count in metrics.department_bottlenecks.values())
    if metrics.high_risk_count >= 2 or metrics.financial_impact_count > 0 or recurring_bottleneck:
        return "at_risk"

    if (
        metrics.correction_count > 0
        or metrics.human_review_count > 0
        or metrics.client_decision_count > 0
        or metrics.medium_risk_count > 0
        or metrics.blocked_count > 0
    ):
        return "attention"

    if metrics.approval_rate >= 0.6 and not metrics.department_bottlenecks:
        return "on_track"

    return "attention"
