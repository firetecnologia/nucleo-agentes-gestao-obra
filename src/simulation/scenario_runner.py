from __future__ import annotations

from pathlib import Path
from typing import Any

from src.agents.orchestrator import OrchestratorAgent
from src.dashboard import build_dashboard_from_dict
from src.domain.models import TaskPayload
from src.events.event_processor import EventProcessor
from src.integrations.asana_client import AsanaClient
from src.integrations.asana_mapping import map_decision_to_asana_operations
from src.reports import build_report_from_dict
from src.storage.repositories import RecordRepository
from src.web.app import create_web_app

from .obra_piloto import default_history_dir
from .scenario_builder import (
    build_dashboard_input,
    build_report_input,
    build_storage_records,
    scenario_events,
    scenario_tasks,
)


class SimulationRunner:
    def __init__(
        self,
        *,
        dry_run: bool = True,
        history_dir: str | Path | None = None,
        orchestrator: OrchestratorAgent | None = None,
        event_processor: EventProcessor | None = None,
    ) -> None:
        self.dry_run = True
        self.history_dir = Path(history_dir) if history_dir else default_history_dir()
        self.orchestrator = orchestrator or OrchestratorAgent()
        self.asana_client = AsanaClient(dry_run=True)
        self.event_processor = event_processor or EventProcessor(
            asana_client=AsanaClient(dry_run=True),
            orchestrator=self.orchestrator,
            dry_run=True,
        )
        self.repository = RecordRepository(self.history_dir)

    def run(self, scenario: dict[str, Any]) -> dict[str, Any]:
        analyses = [self._analyze_task(payload) for payload in scenario_tasks(scenario)]
        events_processed = [self._process_event(event) for event in scenario_events(scenario)]
        planned_operations = _collect_planned_operations(analyses, events_processed)

        report_input = build_report_input(scenario, analyses, events_processed)
        weekly_report = build_report_from_dict(report_input, "weekly_management").to_dict()
        weekly_report["dry_run"] = True
        weekly_report["external_operations"] = []

        dashboard_input = build_dashboard_input(scenario, analyses, events_processed, weekly_report)
        dashboard = build_dashboard_from_dict(dashboard_input).to_dict()
        dashboard["dry_run"] = True
        dashboard["external_operations"] = []

        saved_records = [
            self.repository.save(record)
            for record in build_storage_records(
                scenario,
                analyses,
                events_processed,
                weekly_report,
                dashboard,
            )
        ]
        storage_query = self.repository.query(obra=str(scenario.get("obra", "")))

        return {
            "scenario": scenario.get("scenario", "obra_piloto"),
            "obra": scenario.get("obra", ""),
            "cliente": scenario.get("cliente", ""),
            "analyses": analyses,
            "events_processed": events_processed,
            "planned_operations": planned_operations,
            "weekly_report": weekly_report,
            "dashboard": dashboard,
            "saved_records": saved_records,
            "storage_query": storage_query,
            "web_preview": _build_web_preview(),
            "dry_run": True,
            "external_operations": [],
        }

    def _analyze_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        task = TaskPayload.from_dict(payload)
        decision = self.orchestrator.analyze(task)
        analysis = decision.to_dict()
        analysis.update(
            {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "obra": task.obra,
                "department": task.departamento_responsavel,
                "etapa_obra": task.etapa_obra,
                "impacto_prazo": task.impacto_prazo,
                "impacto_financeiro": task.impacto_financeiro,
                "impacto_cliente": task.impacto_cliente,
            }
        )
        direct_operations = [self.asana_client.post_comment(task.task_id, decision.asana_comment)]
        for next_task in decision.next_tasks:
            direct_operations.append(
                self.asana_client.create_task(
                    name=next_task.name,
                    notes=next_task.description,
                    assignee_gid=next_task.suggested_owner,
                    due_on=next_task.suggested_due,
                )
            )
        mapped_operations = map_decision_to_asana_operations(analysis, payload)
        analysis["planned_operations"] = direct_operations + mapped_operations
        return analysis

    def _process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        result = self.event_processor.process(event).to_dict()
        payload = dict(event.get("task_payload") or {})
        result.update(
            {
                "event_id": event.get("event_id", ""),
                "task_id": event.get("task_id", ""),
                "task_name": payload.get("task_name") or event.get("task_id", ""),
                "obra": payload.get("obra", ""),
                "department": payload.get("departamento_responsavel", ""),
                "impacto_prazo": payload.get("impacto_prazo"),
                "impacto_financeiro": payload.get("impacto_financeiro"),
                "impacto_cliente": payload.get("impacto_cliente"),
            }
        )
        result["dry_run"] = True
        return result


def run_simulation(
    scenario: dict[str, Any],
    *,
    dry_run: bool = True,
    history_dir: str | Path | None = None,
) -> dict[str, Any]:
    return SimulationRunner(dry_run=True, history_dir=history_dir).run(scenario)


def _collect_planned_operations(
    analyses: list[dict[str, Any]],
    events_processed: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    for analysis in analyses:
        operations.extend(analysis.get("planned_operations") or [])
    for event in events_processed:
        operations.extend(event.get("planned_operations") or [])
    return [_force_dry_run(operation) for operation in operations]


def _force_dry_run(operation: dict[str, Any]) -> dict[str, Any]:
    safe_operation = dict(operation)
    safe_operation["dry_run"] = True
    safe_operation.setdefault("external_call", False)
    safe_operation.setdefault("real_action", False)
    return safe_operation


def _build_web_preview() -> dict[str, Any]:
    app = create_web_app()
    routes = ["/", "/dashboard", "/historico-decisoes", "/relatorio-semanal"]
    return {
        "dry_run": True,
        "external_operations": [],
        "routes": [
            {
                "path": route,
                "status_code": app.get(route).status_code,
                "rendered_locally": True,
            }
            for route in routes
        ],
    }
