from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.agents.orchestrator import OrchestratorAgent
from src.domain.models import AgentDecision, TaskPayload
from src.integrations.asana_client import AsanaClient

from .event_log import build_log_entry
from .event_models import AsanaEvent, EventProcessingResult
from .event_router import UnknownEventTypeError, route_event


class EventProcessor:
    def __init__(
        self,
        *,
        asana_client: AsanaClient | None = None,
        orchestrator: OrchestratorAgent | None = None,
        dry_run: bool = True,
    ) -> None:
        self.dry_run = True
        self.asana_client = asana_client or AsanaClient(dry_run=True)
        self.asana_client.dry_run = True
        self.orchestrator = orchestrator or OrchestratorAgent()

    def process(self, raw_event: dict[str, Any] | AsanaEvent) -> EventProcessingResult:
        event = raw_event if isinstance(raw_event, AsanaEvent) else AsanaEvent.from_dict(raw_event)
        effective_dry_run = True

        try:
            route = route_event(event.event_type)
        except UnknownEventTypeError as exc:
            return self._error_result(event, str(exc), dry_run=effective_dry_run)

        handler = getattr(self, route.handler_name)
        return handler(event)

    def _handle_task_ready_for_agent_review(self, event: AsanaEvent) -> EventProcessingResult:
        decision, planned_operations = self._analyze_and_plan(event)
        if decision is None:
            return self._error_result(event, "Payload da tarefa ausente para analise em dry-run.")
        return self._success_result(event, decision, planned_operations)

    def _handle_task_overdue(self, event: AsanaEvent) -> EventProcessingResult:
        decision, planned_operations = self._analyze_and_plan(event)
        if decision is None:
            return self._error_result(event, "Payload da tarefa ausente para alerta de atraso em dry-run.")

        planned_operations.append(
            self.asana_client.post_comment(
                event.task_id,
                "Alerta interno: tarefa vencida identificada. Gestao deve revisar prazo e responsavel.",
            )
        )
        return self._success_result(event, decision, planned_operations)

    def _handle_new_attachment_added(self, event: AsanaEvent) -> EventProcessingResult:
        decision, planned_operations = self._analyze_and_plan(event)
        if decision is None:
            return self._error_result(event, "Payload da tarefa ausente para revalidar evidencias em dry-run.")

        planned_operations.append(
            self.asana_client.post_comment(
                event.task_id,
                "Evidencias revalidadas apos novo anexo. Conferir pendencias antes de avancar.",
            )
        )
        return self._success_result(event, decision, planned_operations)

    def _handle_client_decision_required(self, event: AsanaEvent) -> EventProcessingResult:
        event_with_flag = self._event_with_payload_updates(event, {"precisa_aprovacao_cliente": True})
        decision, planned_operations = self._analyze_and_plan(event_with_flag)
        if decision is None:
            return self._error_result(event, "Payload da tarefa ausente para decisao de cliente em dry-run.")
        return self._success_result(event, decision, planned_operations)

    def _handle_financial_impact_detected(self, event: AsanaEvent) -> EventProcessingResult:
        decision, planned_operations = self._analyze_and_plan(event)
        if decision is None:
            return self._error_result(event, "Payload da tarefa ausente para impacto financeiro em dry-run.")

        planned_operations.append(
            self.asana_client.create_task(
                name=f"Revisar impacto financeiro - {event.task_payload.get('task_name', event.task_id)}",
                notes="Impacto financeiro detectado. Gestao/Financeiro devem revisar antes de qualquer aprovacao.",
                project_id=None,
            )
        )

        forced_decision = deepcopy(decision)
        forced_decision.decision = "escalate_management"
        forced_decision.requires_human_review = True
        return self._success_result(event, forced_decision, planned_operations)

    def _analyze_and_plan(self, event: AsanaEvent) -> tuple[AgentDecision | None, list[dict[str, Any]]]:
        planned_operations = [self.asana_client.fetch_task(event.task_id)]
        if not event.task_payload:
            return None, planned_operations

        task = TaskPayload.from_dict(event.task_payload)
        decision = self.orchestrator.analyze(task)

        planned_operations.append(self.asana_client.post_comment(task.task_id, decision.asana_comment))
        for next_task in decision.next_tasks:
            planned_operations.append(
                self.asana_client.create_task(
                    name=next_task.name,
                    notes=next_task.description,
                    assignee_gid=next_task.suggested_owner,
                    due_on=next_task.suggested_due,
                )
            )

        return decision, planned_operations

    def _success_result(
        self,
        event: AsanaEvent,
        decision: AgentDecision,
        planned_operations: list[dict[str, Any]],
    ) -> EventProcessingResult:
        log_entry = build_log_entry(
            event,
            processed=True,
            dry_run=True,
            decision=decision.decision,
            risk_level=decision.risk_level,
            planned_operations=planned_operations,
        )
        return EventProcessingResult(
            event_type=event.event_type,
            processed=True,
            dry_run=True,
            decision=decision.decision,
            risk_level=decision.risk_level,
            specialist_agent=decision.specialist_agent,
            specialist_analysis=decision.specialist_analysis,
            planned_operations=planned_operations,
            log_entry=log_entry,
            requires_human_review=decision.requires_human_review,
        )

    def _error_result(self, event: AsanaEvent, error: str, *, dry_run: bool = True) -> EventProcessingResult:
        log_entry = build_log_entry(
            event,
            processed=False,
            dry_run=dry_run,
            error=error,
        )
        return EventProcessingResult(
            event_type=event.event_type,
            processed=False,
            dry_run=dry_run,
            planned_operations=[],
            log_entry=log_entry,
            error=error,
        )

    def _event_with_payload_updates(self, event: AsanaEvent, updates: dict[str, Any]) -> AsanaEvent:
        payload = deepcopy(event.task_payload or {})
        payload.update(updates)
        return AsanaEvent(
            event_type=event.event_type,
            task_id=event.task_id,
            event_id=event.event_id,
            occurred_at=event.occurred_at,
            source=event.source,
            dry_run=event.dry_run,
            task_payload=payload,
            metadata=deepcopy(event.metadata),
        )
