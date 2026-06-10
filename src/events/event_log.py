from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .event_models import AsanaEvent


def build_log_entry(
    event: AsanaEvent,
    *,
    processed: bool,
    dry_run: bool,
    decision: str | None = None,
    risk_level: str | None = None,
    planned_operations: list[dict[str, Any]] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    operations = planned_operations or []
    return {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "task_id": event.task_id,
        "source": event.source,
        "processed": processed,
        "dry_run": dry_run,
        "decision": decision,
        "risk_level": risk_level,
        "planned_operations_count": len(operations),
        "error": error,
        "logged_at": datetime.now(UTC).isoformat(),
    }
