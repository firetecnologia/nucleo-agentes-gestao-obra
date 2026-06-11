from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_scenario(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def scenario_tasks(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return list(scenario.get("tasks") or [])


def scenario_events(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    return list(scenario.get("events") or [])


def build_report_input(
    scenario: dict[str, Any],
    analyses: list[dict[str, Any]],
    events_processed: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "obra": scenario.get("obra", ""),
        "periodo": dict(scenario.get("periodo") or {}),
        "items": [_report_item_from_analysis(item) for item in analyses]
        + [_report_item_from_event(item) for item in events_processed if item.get("processed")],
    }


def build_dashboard_input(
    scenario: dict[str, Any],
    analyses: list[dict[str, Any]],
    events_processed: list[dict[str, Any]],
    weekly_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "obra": scenario.get("obra", ""),
        "cliente": scenario.get("cliente", ""),
        "periodo": dict(scenario.get("periodo") or {}),
        "analyses": analyses,
        "events": events_processed,
        "reports": [weekly_report],
    }


def build_storage_records(
    scenario: dict[str, Any],
    analyses: list[dict[str, Any]],
    events_processed: list[dict[str, Any]],
    weekly_report: dict[str, Any],
    dashboard: dict[str, Any],
) -> list[dict[str, Any]]:
    obra = str(scenario.get("obra", ""))
    records: list[dict[str, Any]] = []

    for analysis in analyses:
        records.append(
            {
                "id": f"analysis-{analysis.get('task_id')}",
                "obra": obra,
                "record_type": "analysis",
                "source": "simulation_dry_run",
                "payload": analysis,
            }
        )

    for event in events_processed:
        records.append(
            {
                "id": f"event-{event.get('event_id')}",
                "obra": obra,
                "record_type": "event",
                "source": "simulation_dry_run",
                "payload": event,
            }
        )

    records.extend(
        [
            {
                "id": "report-weekly-management",
                "obra": obra,
                "record_type": "report",
                "source": "simulation_dry_run",
                "payload": weekly_report,
            },
            {
                "id": "dashboard-obra-piloto",
                "obra": obra,
                "record_type": "dashboard",
                "source": "simulation_dry_run",
                "payload": dashboard,
            },
        ]
    )

    for index, entry in enumerate(dashboard.get("decision_history") or [], start=1):
        records.append(
            {
                "id": f"decision-history-{index:03d}",
                "obra": obra,
                "record_type": "decision_history",
                "source": "simulation_dry_run",
                "payload": entry,
            }
        )

    return records


def _report_item_from_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": analysis.get("task_id", ""),
        "task_name": analysis.get("task_name", ""),
        "department": analysis.get("department", ""),
        "decision": analysis.get("decision", ""),
        "risk_level": analysis.get("risk_level", "low"),
        "requires_human_review": bool(analysis.get("requires_human_review", False)),
        "specialist_agent": analysis.get("specialist_agent"),
        "recommended_actions": list(analysis.get("recommended_actions") or []),
        "missing_evidence": list(analysis.get("missing_evidence") or []),
        "planned_operations": list(analysis.get("planned_operations") or []),
        "impacto_prazo": analysis.get("impacto_prazo"),
        "impacto_financeiro": analysis.get("impacto_financeiro"),
        "impacto_cliente": analysis.get("impacto_cliente"),
    }


def _report_item_from_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": event.get("task_id", ""),
        "task_name": event.get("task_name") or event.get("task_id", ""),
        "department": event.get("department", ""),
        "decision": event.get("decision", "monitor"),
        "risk_level": event.get("risk_level", "low"),
        "requires_human_review": bool(event.get("requires_human_review", False)),
        "specialist_agent": event.get("specialist_agent"),
        "recommended_actions": _event_recommended_actions(event),
        "missing_evidence": [],
        "planned_operations": list(event.get("planned_operations") or []),
        "impacto_prazo": event.get("impacto_prazo"),
        "impacto_financeiro": event.get("impacto_financeiro"),
        "impacto_cliente": event.get("impacto_cliente"),
    }


def _event_recommended_actions(event: dict[str, Any]) -> list[str]:
    if event.get("event_type") == "financial_impact_detected":
        return ["Gestao deve revisar impacto financeiro antes de qualquer aprovacao."]
    if event.get("event_type") == "client_decision_required":
        return ["Atendimento deve preparar decisao de cliente para revisao humana."]
    return ["Equipe deve revisar evento processado em dry-run."]
