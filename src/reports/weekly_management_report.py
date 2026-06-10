from __future__ import annotations

from .report_models import ReportInput, ReportOutput


def build_weekly_management_report(report_input: ReportInput) -> ReportOutput:
    from .report_builder import (
        build_summary,
        classify_health_status,
        consolidate_department_bottlenecks,
        list_active_risks,
        list_deadline_impacts,
        list_financial_impacts,
        list_pending_decisions,
        list_recommended_actions,
    )

    items = report_input.items
    health_status = classify_health_status(items)
    approved_or_progress = [
        item.short_label()
        for item in items
        if item.decision in {"approved", "create_next_tasks", "monitor"}
    ]
    recommended_actions = list_recommended_actions(items)

    return ReportOutput(
        report_type="weekly_management",
        obra=report_input.obra,
        health_status=health_status,
        summary=build_summary(report_input.obra, health_status, items),
        period=report_input.periodo.to_dict(),
        highlights=approved_or_progress,
        risks=list_active_risks(items),
        pending_decisions=list_pending_decisions(items),
        department_bottlenecks=consolidate_department_bottlenecks(items),
        recommended_actions=recommended_actions,
        requires_human_review=True,
        deadline_impacts=list_deadline_impacts(items),
        financial_impacts=list_financial_impacts(items),
        management_decisions=list_pending_decisions(items),
    )
