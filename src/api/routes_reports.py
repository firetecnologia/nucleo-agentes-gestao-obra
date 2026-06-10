from __future__ import annotations

from typing import Any

from src.reports import build_report_from_dict

from .schemas import extract_report_payload


def generate_report_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    report_payload, report_type = extract_report_payload(payload)
    report = build_report_from_dict(report_payload, report_type)  # type: ignore[arg-type]
    output = report.to_dict()
    output["dry_run"] = True
    output["external_operations"] = []
    return output
