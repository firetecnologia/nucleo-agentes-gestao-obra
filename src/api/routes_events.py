from __future__ import annotations

from typing import Any

from src.events.event_processor import EventProcessor


def process_event_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    result = EventProcessor(dry_run=True).process(payload)
    output = result.to_dict()
    output["dry_run"] = True
    output["external_operations"] = []
    return output
