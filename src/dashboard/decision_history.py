from __future__ import annotations

from typing import Any, Iterable
import unicodedata

from .dashboard_models import DecisionHistoryEntry


PENDING_DECISIONS = {"blocked", "escalate_management", "ask_client", "request_correction"}


def build_decision_history(
    *,
    analyses: Iterable[dict[str, Any]] | None = None,
    events: Iterable[dict[str, Any]] | None = None,
    reports: Iterable[dict[str, Any]] | None = None,
) -> list[DecisionHistoryEntry]:
    history: list[DecisionHistoryEntry] = []

    for analysis in analyses or []:
        history.append(_entry_from_analysis(analysis))

    for event in events or []:
        history.append(_entry_from_event(event))

    for report in reports or []:
        history.extend(_entries_from_report(report))

    return sort_decision_history(_dedupe_history(history))


def sort_decision_history(history: Iterable[DecisionHistoryEntry]) -> list[DecisionHistoryEntry]:
    indexed = list(enumerate(history))
    indexed.sort(
        key=lambda item: (
            item[1].created_at is None,
            item[1].created_at or "",
            item[0],
        )
    )
    return [entry for _, entry in indexed]


def filter_decision_history(
    history: Iterable[DecisionHistoryEntry],
    *,
    department: str | None = None,
    risk_level: str | None = None,
    decision: str | None = None,
) -> list[DecisionHistoryEntry]:
    department_key = _normalize(department)
    risk_key = _normalize(risk_level)
    decision_key = _normalize(decision)

    filtered: list[DecisionHistoryEntry] = []
    for entry in history:
        if department_key and _normalize(entry.department) != department_key:
            continue
        if risk_key and _normalize(entry.risk_level) != risk_key:
            continue
        if decision_key and _normalize(entry.decision) != decision_key:
            continue
        filtered.append(entry)
    return filtered


def filter_history_by_department(
    history: Iterable[DecisionHistoryEntry],
    department: str,
) -> list[DecisionHistoryEntry]:
    return filter_decision_history(history, department=department)


def filter_history_by_risk(
    history: Iterable[DecisionHistoryEntry],
    risk_level: str,
) -> list[DecisionHistoryEntry]:
    return filter_decision_history(history, risk_level=risk_level)


def filter_history_by_decision(
    history: Iterable[DecisionHistoryEntry],
    decision: str,
) -> list[DecisionHistoryEntry]:
    return filter_decision_history(history, decision=decision)


def consolidate_pending_decisions(
    history: Iterable[DecisionHistoryEntry],
) -> list[DecisionHistoryEntry]:
    return [
        entry
        for entry in history
        if entry.decision in PENDING_DECISIONS or entry.requires_human_review
    ]


def latest_decisions_by_task(
    history: Iterable[DecisionHistoryEntry],
) -> list[DecisionHistoryEntry]:
    latest: dict[str, DecisionHistoryEntry] = {}
    without_task_id: list[DecisionHistoryEntry] = []

    for index, entry in enumerate(sort_decision_history(history)):
        if entry.task_id:
            latest[entry.task_id] = entry
        else:
            without_task_id.append(
                DecisionHistoryEntry(
                    task_id=f"sem-id-{index}",
                    task_name=entry.task_name,
                    department=entry.department,
                    decision=entry.decision,
                    risk_level=entry.risk_level,
                    specialist_agent=entry.specialist_agent,
                    requires_human_review=entry.requires_human_review,
                    source=entry.source,
                    created_at=entry.created_at,
                )
            )

    return sort_decision_history([*latest.values(), *without_task_id])


def _entry_from_analysis(data: dict[str, Any]) -> DecisionHistoryEntry:
    return DecisionHistoryEntry(
        task_id=str(data.get("task_id", "")),
        task_name=str(data.get("task_name") or data.get("name") or ""),
        department=str(data.get("department") or data.get("departamento_responsavel") or ""),
        decision=str(data.get("decision") or "monitor"),
        risk_level=str(data.get("risk_level") or "low"),
        specialist_agent=data.get("specialist_agent"),
        requires_human_review=bool(data.get("requires_human_review", False)),
        source="analysis",
        created_at=_first_text(data, "created_at", "analyzed_at", "updated_at"),
    )


def _entry_from_event(data: dict[str, Any]) -> DecisionHistoryEntry:
    log_entry = data.get("log_entry") or {}
    task_payload = data.get("task_payload") or {}

    return DecisionHistoryEntry(
        task_id=str(data.get("task_id") or log_entry.get("task_id") or task_payload.get("task_id") or ""),
        task_name=str(
            data.get("task_name")
            or task_payload.get("task_name")
            or log_entry.get("task_name")
            or ""
        ),
        department=str(
            data.get("department")
            or task_payload.get("department")
            or task_payload.get("departamento_responsavel")
            or log_entry.get("department")
            or ""
        ),
        decision=str(data.get("decision") or log_entry.get("decision") or "monitor"),
        risk_level=str(data.get("risk_level") or log_entry.get("risk_level") or "low"),
        specialist_agent=data.get("specialist_agent"),
        requires_human_review=bool(data.get("requires_human_review", False)),
        source="event",
        created_at=(
            _first_text(data, "created_at", "occurred_at")
            or _first_text(log_entry, "logged_at", "created_at")
        ),
    )


def _entries_from_report(data: dict[str, Any]) -> list[DecisionHistoryEntry]:
    created_at = (
        _first_text(data, "created_at", "data_referencia")
        or _first_text(data.get("period") or {}, "fim")
        or _first_text(data.get("periodo") or {}, "fim")
    )
    items = list(data.get("tasks_analyzed") or data.get("items") or [])
    entries: list[DecisionHistoryEntry] = []

    for item in items:
        entries.append(
            DecisionHistoryEntry(
                task_id=str(item.get("task_id", "")),
                task_name=str(item.get("task_name") or item.get("name") or ""),
                department=str(item.get("department") or item.get("departamento_responsavel") or ""),
                decision=str(item.get("decision") or "monitor"),
                risk_level=str(item.get("risk_level") or "low"),
                specialist_agent=item.get("specialist_agent"),
                requires_human_review=bool(item.get("requires_human_review", False)),
                source="report",
                created_at=created_at,
            )
        )

    return entries


def _dedupe_history(history: Iterable[DecisionHistoryEntry]) -> list[DecisionHistoryEntry]:
    deduped: list[DecisionHistoryEntry] = []
    seen: set[tuple[str, str, str, str, str | None]] = set()
    for entry in history:
        key = (entry.source, entry.task_id, entry.task_name, entry.decision, entry.created_at)
        if key not in seen:
            deduped.append(entry)
            seen.add(key)
    return deduped


def _first_text(data: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if value:
            return str(value)
    return None


def _normalize(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(char for char in text if not unicodedata.combining(char))
