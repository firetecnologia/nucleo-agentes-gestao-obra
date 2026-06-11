from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class PlannedAsanaOperation:
    operation: str
    payload: dict[str, Any]
    dry_run: bool = True
    source: str = "asana_sandbox_mapping"
    external_call: bool = False
    real_action: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["dry_run"] = True
        data["external_call"] = False
        data["real_action"] = False
        return data


@dataclass(slots=True)
class AsanaTaskReference:
    task_id: str
    task_name: str
    obra: str
    department: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_sources(
        cls,
        decision: dict[str, Any],
        task_payload: dict[str, Any] | None = None,
    ) -> "AsanaTaskReference":
        payload = task_payload or {}
        return cls(
            task_id=str(decision.get("task_id") or payload.get("task_id") or ""),
            task_name=str(decision.get("task_name") or payload.get("task_name") or ""),
            obra=str(decision.get("obra") or payload.get("obra") or ""),
            department=str(
                decision.get("department")
                or decision.get("departamento_responsavel")
                or payload.get("department")
                or payload.get("departamento_responsavel")
                or ""
            ),
            metadata={
                "decision": decision.get("decision"),
                "risk_level": decision.get("risk_level"),
                "specialist_agent": decision.get("specialist_agent"),
            },
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
