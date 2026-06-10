from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


RecordType = Literal["analysis", "event", "report", "dashboard", "decision_history"]
VALID_RECORD_TYPES: set[str] = {"analysis", "event", "report", "dashboard", "decision_history"}


@dataclass(slots=True)
class StorageRecord:
    id: str
    obra: str
    record_type: RecordType
    created_at: str
    source: str = "local_dry_run"
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StorageRecord":
        record_type = str(data.get("record_type", "analysis"))
        if record_type not in VALID_RECORD_TYPES:
            raise ValueError(f"Tipo de registro nao suportado: {record_type}")

        return cls(
            id=str(data.get("id") or uuid4()),
            obra=str(data.get("obra", "")),
            record_type=record_type,  # type: ignore[arg-type]
            created_at=str(data.get("created_at") or utc_now_iso()),
            source=str(data.get("source") or "local_dry_run"),
            payload=dict(data.get("payload") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StorageQuery:
    obra: str | None = None
    record_type: RecordType | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StorageQuery":
        record_type = data.get("record_type")
        if record_type and record_type not in VALID_RECORD_TYPES:
            raise ValueError(f"Tipo de registro nao suportado: {record_type}")
        return cls(
            obra=data.get("obra"),
            record_type=record_type,
        )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
