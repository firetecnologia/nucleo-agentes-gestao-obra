from __future__ import annotations

from typing import Any

from src.dashboard import build_dashboard_from_dict


def generate_dashboard_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    dashboard = build_dashboard_from_dict(payload)
    output = dashboard.to_dict()
    output["dry_run"] = True
    output["external_operations"] = []
    return output
