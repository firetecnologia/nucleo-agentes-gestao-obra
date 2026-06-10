from __future__ import annotations

import unicodedata

from .report_models import ClientDraft, ReportInput, ReportOutput


FORBIDDEN_REPLACEMENTS = {
    "conflito interno": "ponto tecnico em avaliacao",
    "desorganizacao": "ajuste operacional",
    "erro interno": "ajuste tecnico",
    "falha interna": "ajuste tecnico",
    "atraso critico": "ponto de atencao de prazo",
    "bloqueio": "pendencia de validacao",
}


def build_client_report_draft(report_input: ReportInput) -> ReportOutput:
    from .report_builder import (
        build_summary,
        classify_health_status,
        consolidate_department_bottlenecks,
        list_pending_decisions,
        list_recommended_actions,
    )

    items = report_input.items
    health_status = classify_health_status(items)
    client_decisions = [
        _safe_text(item.short_label())
        for item in items
        if item.decision == "ask_client" or _normalize_client(item.impacto_cliente) in {"medio", "alto", "critico"}
    ]
    next_steps = _client_next_steps(items)
    communicable_risks = _client_communicable_risks(items)
    summary = _safe_text(
        f"A obra {report_input.obra} segue em acompanhamento ativo, com {len(items)} tarefa(s) analisada(s) no periodo."
    )
    control_phrase = (
        "Seguimos acompanhando os proximos passos com controle, previsibilidade e registro das decisoes."
    )
    body = _build_body(summary, next_steps, client_decisions, communicable_risks, control_phrase)
    client_draft = ClientDraft(
        summary=summary,
        next_steps=next_steps,
        pending_client_decisions=client_decisions,
        communicable_risks=communicable_risks,
        control_phrase=control_phrase,
        body=body,
    )

    return ReportOutput(
        report_type="client_draft",
        obra=report_input.obra,
        health_status=health_status,
        summary=summary,
        period=report_input.periodo.to_dict(),
        highlights=_client_highlights(items),
        risks=communicable_risks,
        pending_decisions=_safe_list(list_pending_decisions(items)),
        department_bottlenecks=consolidate_department_bottlenecks(items),
        recommended_actions=_safe_list(list_recommended_actions(items)),
        client_draft=client_draft,
        requires_human_review=True,
        external_operations=[],
    )


def _client_highlights(items) -> list[str]:
    highlights = [
        _safe_text(f"{item.task_name}: etapa acompanhada")
        for item in items
        if item.decision in {"approved", "create_next_tasks", "monitor"}
    ]
    return highlights or ["Andamento acompanhado pela equipe tecnica."]


def _client_next_steps(items) -> list[str]:
    steps: list[str] = []
    if any(item.decision == "request_correction" for item in items):
        steps.append("Concluir validacoes tecnicas e evidencias complementares.")
    if any(item.decision == "ask_client" for item in items):
        steps.append("Formalizar decisao pendente do cliente apos revisao interna.")
    if any(item.decision in {"approved", "create_next_tasks"} for item in items):
        steps.append("Dar continuidade as proximas etapas planejadas.")
    return [_safe_text(step) for step in (steps or ["Manter acompanhamento e registro das proximas etapas."])]


def _client_communicable_risks(items) -> list[str]:
    risks: list[str] = []
    if any(item.risk_level in {"medium", "high", "critical"} for item in items):
        risks.append("Existem pontos de atencao tecnico-operacionais em acompanhamento pela equipe.")
    if any(_normalize_client(item.impacto_prazo) in {"medio", "alto", "critico"} for item in items):
        risks.append("O cronograma esta sendo monitorado para preservar previsibilidade.")
    if any(_normalize_client(item.impacto_cliente) in {"medio", "alto", "critico"} for item in items):
        risks.append("Ha decisoes que podem exigir alinhamento formal com o cliente.")
    return [_safe_text(risk) for risk in (risks or ["Nao ha riscos comunicaveis relevantes neste momento."])]


def _build_body(
    summary: str,
    next_steps: list[str],
    client_decisions: list[str],
    communicable_risks: list[str],
    control_phrase: str,
) -> str:
    decisions_text = (
        "Decisoes pendentes do cliente: " + "; ".join(client_decisions)
        if client_decisions
        else "Nao ha decisao pendente do cliente neste rascunho."
    )
    return _safe_text(
        "Prezados, segue rascunho para revisao interna antes de qualquer envio. "
        f"{summary} "
        f"Proximos passos: {'; '.join(next_steps)}. "
        f"{decisions_text} "
        f"Pontos de atencao comunicaveis: {'; '.join(communicable_risks)}. "
        f"{control_phrase}"
    )


def _safe_text(value: str) -> str:
    text = _strip_accents(value)
    lowered = text.lower()
    for forbidden, replacement in FORBIDDEN_REPLACEMENTS.items():
        if forbidden in lowered:
            text = _replace_case_insensitive(text, forbidden, replacement)
            lowered = text.lower()
    return text


def _normalize_client(value: str | None) -> str:
    return _strip_accents(value or "").lower().strip()


def _strip_accents(value: str) -> str:
    text = unicodedata.normalize("NFKD", value)
    return "".join(char for char in text if not unicodedata.combining(char))


def _safe_list(values: list[str]) -> list[str]:
    return [_safe_text(value) for value in values]


def _replace_case_insensitive(value: str, old: str, new: str) -> str:
    start = value.lower().find(old.lower())
    while start >= 0:
        end = start + len(old)
        value = value[:start] + new + value[end:]
        start = value.lower().find(old.lower())
    return value
