from __future__ import annotations

from .report_models import ReportInput, ReportOutput


def build_internal_daily_report(report_input: ReportInput) -> ReportOutput:
    from .report_builder import (
        build_summary,
        classify_health_status,
        consolidate_department_bottlenecks,
        consolidate_department_pending,
        list_active_risks,
        list_pending_decisions,
        list_recommended_actions,
        summarize_tasks,
    )

    items = report_input.items
    health_status = classify_health_status(items)
    approved_tasks = [item.short_label() for item in items if item.decision == "approved"]
    correction_tasks = [item.short_label() for item in items if item.decision == "request_correction"]
    blocked_tasks = [item.short_label() for item in items if item.decision == "blocked"]
    pending_decisions = list_pending_decisions(items)
    recommended_actions = list_recommended_actions(items)

    return ReportOutput(
        report_type="internal_daily",
        obra=report_input.obra,
        health_status=health_status,
        summary=build_summary(report_input.obra, health_status, items),
        period=report_input.periodo.to_dict(),
        highlights=approved_tasks,
        risks=list_active_risks(items),
        pending_decisions=pending_decisions,
        department_bottlenecks=consolidate_department_bottlenecks(items),
        recommended_actions=recommended_actions,
        requires_human_review=bool(pending_decisions),
        tasks_analyzed=summarize_tasks(items),
        approved_tasks=approved_tasks,
        correction_requested_tasks=correction_tasks,
        blocked_tasks=blocked_tasks,
        active_risks=list_active_risks(items),
        department_pending=consolidate_department_pending(items),
        next_actions=recommended_actions,
        management_decisions=[
            decision
            for decision in pending_decisions
            if "escalate_management" in decision or "blocked" in decision
        ],
    )
