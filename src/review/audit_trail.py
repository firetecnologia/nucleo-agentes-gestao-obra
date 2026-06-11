from __future__ import annotations

from typing import Any

from src.storage.storage_models import utc_now_iso


def build_audit_entry(
    *,
    action: str,
    status: str,
    reviewer: str = "",
    notes: str = "",
    previous_status: str | None = None,
) -> dict[str, Any]:
    entry = {
        "action": action,
        "status": status,
        "reviewer": reviewer,
        "notes": notes,
        "created_at": utc_now_iso(),
        "dry_run": True,
        "external_operations": [],
    }
    if previous_status is not None:
        entry["previous_status"] = previous_status
    return entry


def append_audit_entry(review: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    updated = dict(review)
    audit_trail = list(updated.get("audit_trail") or [])
    safe_entry = dict(entry)
    safe_entry["dry_run"] = True
    safe_entry["external_operations"] = []
    audit_trail.append(safe_entry)
    updated["audit_trail"] = audit_trail
    return updated
