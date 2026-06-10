from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


HttpMethod = Literal["GET", "POST"]


@dataclass(slots=True)
class ApiResponse:
    status_code: int
    body: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code,
            "body": self.body,
        }


@dataclass(slots=True)
class RouteDefinition:
    method: HttpMethod
    path: str
    handler_name: str
    description: str
    dry_run: bool = True
    external_operations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "path": self.path,
            "handler_name": self.handler_name,
            "description": self.description,
            "dry_run": True,
            "external_operations": [],
        }


def response(body: dict[str, Any], *, status_code: int = 200) -> ApiResponse:
    safe_body = dict(body)
    safe_body["dry_run"] = True
    safe_body.setdefault("external_operations", [])
    return ApiResponse(status_code=status_code, body=safe_body)


def extract_report_payload(data: dict[str, Any]) -> tuple[dict[str, Any], str]:
    report_type = str(data.get("report_type") or data.get("type") or "weekly_management")
    payload = data.get("payload") or data.get("data") or {
        key: value
        for key, value in data.items()
        if key not in {"report_type", "type", "dry_run", "external_operations"}
    }
    return dict(payload), report_type
