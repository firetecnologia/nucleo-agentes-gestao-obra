from __future__ import annotations

from dataclasses import dataclass

from .event_models import KNOWN_EVENT_TYPES


class UnknownEventTypeError(ValueError):
    """Erro controlado para eventos ainda não suportados."""


@dataclass(frozen=True, slots=True)
class EventRoute:
    event_type: str
    handler_name: str
    description: str


EVENT_ROUTES: dict[str, EventRoute] = {
    "task_ready_for_agent_review": EventRoute(
        event_type="task_ready_for_agent_review",
        handler_name="_handle_task_ready_for_agent_review",
        description="Tarefa pronta para análise do agente.",
    ),
    "task_overdue": EventRoute(
        event_type="task_overdue",
        handler_name="_handle_task_overdue",
        description="Tarefa vencida e não concluída.",
    ),
    "new_attachment_added": EventRoute(
        event_type="new_attachment_added",
        handler_name="_handle_new_attachment_added",
        description="Novo anexo incluído na tarefa.",
    ),
    "client_decision_required": EventRoute(
        event_type="client_decision_required",
        handler_name="_handle_client_decision_required",
        description="Aprovação do cliente exigida.",
    ),
    "financial_impact_detected": EventRoute(
        event_type="financial_impact_detected",
        handler_name="_handle_financial_impact_detected",
        description="Impacto financeiro detectado.",
    ),
}


def route_event(event_type: str) -> EventRoute:
    if event_type not in KNOWN_EVENT_TYPES:
        raise UnknownEventTypeError(f"Tipo de evento desconhecido: {event_type or 'não informado'}")
    return EVENT_ROUTES[event_type]
