from __future__ import annotations

from typing import Any, Iterable

from .asana_operations import (
    planned_field_update,
    planned_human_review,
    planned_internal_comment,
    planned_internal_task,
    planned_task_link,
)
from .asana_payloads import AsanaTaskReference


def map_decision_to_asana_operations(
    decision: dict[str, Any],
    task_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    reference = AsanaTaskReference.from_sources(decision, task_payload)
    decision_name = str(decision.get("decision") or "monitor")
    operations: list[dict[str, Any]] = [
        planned_task_link(reference, target_department=_next_department(decision, task_payload)),
    ]

    if decision_name == "request_correction":
        operations.extend(_map_request_correction(decision, reference))
    elif decision_name == "ask_client":
        operations.extend(_map_ask_client(decision, reference))
    elif decision_name == "escalate_management":
        operations.extend(_map_escalate_management(decision, reference))
    elif decision_name == "create_next_tasks":
        operations.extend(_map_create_next_tasks(decision, reference, task_payload))
    elif decision_name == "blocked":
        operations.extend(_map_blocked(decision, reference))
    elif decision_name == "approved":
        operations.append(
            planned_field_update(
                reference,
                {"status_agente": "Aprovado em dry-run"},
                reason="Registrar aprovacao planejada sem chamada real.",
            )
        )
    else:
        operations.append(
            planned_field_update(
                reference,
                {"status_agente": "Monitoramento em dry-run"},
                reason="Registrar monitoramento planejado sem chamada real.",
            )
        )

    if bool(decision.get("requires_human_review", False)) and not _has_operation(
        operations,
        "planned_human_review",
    ):
        operations.append(
            planned_human_review(
                reference,
                review_reason="Decisao marcada para revisao humana.",
            )
        )

    return [_force_sandbox(operation) for operation in operations]


def map_decisions_to_asana_operations(
    decisions: Iterable[dict[str, Any]],
    task_payloads: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    payloads = list(task_payloads or [])
    operations: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions):
        payload = payloads[index] if index < len(payloads) else None
        operations.extend(map_decision_to_asana_operations(decision, payload))
    return operations


def _map_request_correction(
    decision: dict[str, Any],
    reference: AsanaTaskReference,
) -> list[dict[str, Any]]:
    missing = ", ".join(decision.get("missing_evidence") or []) or "evidencias pendentes"
    return [
        planned_internal_comment(
            reference,
            f"Correcao solicitada em dry-run. Pendencias: {missing}.",
            reason="Mapear request_correction para comentario interno planejado.",
        ),
        planned_field_update(
            reference,
            {"status_agente": "Correcao solicitada", "risco_agente": decision.get("risk_level", "low")},
            reason="Atualizar campos planejados da tarefa sem chamada real.",
        ),
    ]


def _map_ask_client(
    decision: dict[str, Any],
    reference: AsanaTaskReference,
) -> list[dict[str, Any]]:
    return [
        planned_internal_task(
            reference,
            name=f"Revisar comunicacao com cliente - {reference.task_name or reference.task_id}",
            notes=(
                "Preparar decisao de cliente apenas para revisao humana. "
                "Nenhuma mensagem deve ser enviada automaticamente."
            ),
            department="Atendimento",
            reason="Mapear ask_client para tarefa interna de revisao.",
        ),
        planned_human_review(
            reference,
            review_reason="Decisao depende de cliente e precisa revisao antes de qualquer comunicacao.",
            reviewer_group="Atendimento/Gestao",
        ),
    ]


def _map_escalate_management(
    decision: dict[str, Any],
    reference: AsanaTaskReference,
) -> list[dict[str, Any]]:
    return [
        planned_internal_task(
            reference,
            name=f"Revisar decisao de gestao - {reference.task_name or reference.task_id}",
            notes="Gestao deve revisar impacto, risco e proximo passo antes de qualquer aprovacao.",
            department="Gestao",
            reason="Mapear escalate_management para tarefa interna de gestao.",
        ),
        planned_human_review(
            reference,
            review_reason="Decisao escalada para gestao.",
            reviewer_group="Gestao",
        ),
    ]


def _map_create_next_tasks(
    decision: dict[str, Any],
    reference: AsanaTaskReference,
    task_payload: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    next_tasks = list(decision.get("next_tasks") or [])
    if not next_tasks:
        next_department = _next_department(decision, task_payload) or "Proximo departamento"
        next_tasks = [
            {
                "name": f"Dar continuidade - {reference.task_name or reference.task_id}",
                "department": next_department,
                "description": "Tarefa planejada para continuidade da obra em dry-run.",
            }
        ]

    operations: list[dict[str, Any]] = []
    for next_task in next_tasks:
        operations.append(
            planned_internal_task(
                reference,
                name=str(next_task.get("name") or "Proxima tarefa planejada"),
                notes=str(next_task.get("description") or "Tarefa planejada em dry-run."),
                department=str(next_task.get("department") or _next_department(decision, task_payload) or ""),
                reason="Mapear create_next_tasks para tarefa planejada do proximo departamento.",
            )
        )
    return operations


def _map_blocked(
    decision: dict[str, Any],
    reference: AsanaTaskReference,
) -> list[dict[str, Any]]:
    return [
        planned_internal_comment(
            reference,
            "Bloqueio identificado em dry-run. Gestao deve revisar antes de avancar.",
            reason="Registrar bloqueio planejado sem chamada real.",
        ),
        planned_human_review(
            reference,
            review_reason="Bloqueio ativo exige revisao humana.",
            reviewer_group="Gestao",
        ),
    ]


def _next_department(
    decision: dict[str, Any],
    task_payload: dict[str, Any] | None,
) -> str | None:
    payload = task_payload or {}
    return (
        decision.get("proximo_departamento")
        or decision.get("next_department")
        or payload.get("proximo_departamento")
    )


def _has_operation(operations: list[dict[str, Any]], operation_name: str) -> bool:
    return any(operation.get("operation") == operation_name for operation in operations)


def _force_sandbox(operation: dict[str, Any]) -> dict[str, Any]:
    safe_operation = dict(operation)
    safe_operation["dry_run"] = True
    safe_operation["external_call"] = False
    safe_operation["real_action"] = False
    safe_operation.setdefault("source", "asana_sandbox_mapping")
    return safe_operation
