from __future__ import annotations

from typing import Any, Iterable

from .dashboard_models import DashboardInput, DashboardOutput, DecisionHistoryEntry
from .decision_history import build_decision_history, consolidate_pending_decisions
from .metrics import build_department_summary, calculate_metrics
from .work_health import calculate_work_health


def build_dashboard_from_dict(data: dict[str, Any]) -> DashboardOutput:
    return build_dashboard(DashboardInput.from_dict(data))


def build_dashboard(dashboard_input: DashboardInput) -> DashboardOutput:
    history = build_decision_history(
        analyses=dashboard_input.analyses,
        events=dashboard_input.events,
        reports=dashboard_input.reports,
    )
    metrics = calculate_metrics(
        history,
        analyses=dashboard_input.analyses,
        events=dashboard_input.events,
        reports=dashboard_input.reports,
    )
    health_status = calculate_work_health(metrics, history)

    return DashboardOutput(
        obra=dashboard_input.obra,
        cliente=dashboard_input.cliente,
        health_status=health_status,
        metrics=metrics,
        decision_history=history,
        active_risks=list_active_risks(history),
        pending_decisions=[
            entry.to_dict() for entry in consolidate_pending_decisions(history)
        ],
        department_summary=build_department_summary(history, metrics),
        recommended_management_actions=list_recommended_management_actions(
            dashboard_input.analyses,
            dashboard_input.events,
            dashboard_input.reports,
            metrics.department_bottlenecks,
        ),
        period=dashboard_input.periodo.to_dict(),
        dry_run=True,
        external_operations=[],
    )


def list_active_risks(history: Iterable[DecisionHistoryEntry]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for entry in history:
        if entry.risk_level in {"medium", "high", "critical"} or entry.decision == "blocked":
            risks.append(
                {
                    "task_id": entry.task_id,
                    "task_name": entry.task_name,
                    "department": entry.department,
                    "risk_level": entry.risk_level,
                    "decision": entry.decision,
                    "source": entry.source,
                    "created_at": entry.created_at,
                }
            )
    return _dedupe_dicts(risks)


def list_recommended_management_actions(
    analyses: Iterable[dict[str, Any]],
    events: Iterable[dict[str, Any]],
    reports: Iterable[dict[str, Any]],
    department_bottlenecks: dict[str, int],
) -> list[str]:
    actions: list[str] = []

    for item in analyses:
        actions.extend(str(action) for action in item.get("recommended_actions") or [])

    for event in events:
        if event.get("event_type") == "financial_impact_detected":
            actions.append("Revisar impacto financeiro antes de qualquer aprovacao.")
        if event.get("event_type") == "client_decision_required":
            actions.append("Preparar decisao de cliente apenas para revisao humana.")

    for report in reports:
        actions.extend(str(action) for action in report.get("recommended_actions") or [])
        actions.extend(str(action) for action in report.get("management_decisions") or [])

    for department, count in department_bottlenecks.items():
        if count >= 2:
            actions.append(f"Priorizar destravamento do departamento {department}.")

    if not actions:
        actions.append("Manter acompanhamento em dry-run e revisar novas evidencias da obra.")

    return _dedupe_strings(actions)


def _dedupe_strings(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value and value not in deduped:
            deduped.append(value)
    return deduped


def _dedupe_dicts(values: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for value in values:
        key = (
            value.get("task_id"),
            value.get("risk_level"),
            value.get("decision"),
            value.get("source"),
            value.get("created_at"),
        )
        if key not in seen:
            deduped.append(value)
            seen.add(key)
    return deduped
