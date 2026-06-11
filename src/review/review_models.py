from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from src.storage.storage_models import utc_now_iso


ReviewStatus = Literal["pending", "approved", "rejected", "changes_requested"]
VALID_REVIEW_STATUSES: set[str] = {"pending", "approved", "rejected", "changes_requested"}


@dataclass(slots=True)
class ReviewItem:
    review_id: str
    obra: str
    task_id: str
    decision: str
    risk_level: str
    reason: str
    status: ReviewStatus = "pending"
    reviewer: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    reviewed_at: str = ""
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReviewItem":
        status = str(data.get("status") or "pending")
        validate_review_status(status)
        return cls(
            review_id=str(data.get("review_id") or ""),
            obra=str(data.get("obra") or ""),
            task_id=str(data.get("task_id") or ""),
            decision=str(data.get("decision") or ""),
            risk_level=str(data.get("risk_level") or "low"),
            reason=str(data.get("reason") or ""),
            status=status,  # type: ignore[arg-type]
            reviewer=str(data.get("reviewer") or ""),
            created_at=str(data.get("created_at") or utc_now_iso()),
            reviewed_at=str(data.get("reviewed_at") or ""),
            audit_trail=list(data.get("audit_trail") or []),
        )

    def to_dict(self) -> dict[str, Any]:
        output = asdict(self)
        output["dry_run"] = True
        output["external_operations"] = []
        return output


def validate_review_status(status: str) -> None:
    if status not in VALID_REVIEW_STATUSES:
        raise ValueError(f"Status de revisao invalido: {status}")
