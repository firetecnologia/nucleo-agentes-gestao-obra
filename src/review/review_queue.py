from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
import unicodedata

from src.storage.storage_models import utc_now_iso

from .approval_rules import create_review_item_from_decision
from .audit_trail import build_audit_entry
from .review_models import ReviewItem, ReviewStatus, validate_review_status


class ReviewQueue:
    def __init__(self, base_dir: str | Path = "local_data/reviews") -> None:
        self.base_dir = Path(base_dir)

    def add_decision(
        self,
        decision: dict[str, Any],
        *,
        review_id: str | None = None,
    ) -> dict[str, Any] | None:
        item = create_review_item_from_decision(
            decision,
            review_id=review_id or self.next_review_id(),
        )
        if item is None:
            return None
        self._save(item)
        return item.to_dict()

    def list_reviews(self, *, status: str | None = None) -> dict[str, Any]:
        if status:
            validate_review_status(status)
        reviews = [item.to_dict() for item in self._load_all()]
        if status:
            reviews = [item for item in reviews if item["status"] == status]
        return {
            "dry_run": True,
            "external_operations": [],
            "count": len(reviews),
            "reviews": reviews,
        }

    def get(self, review_id: str) -> ReviewItem:
        path = self._path(review_id)
        if not path.exists():
            raise FileNotFoundError(f"Revisao nao encontrada: {review_id}")
        return ReviewItem.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def update_status(
        self,
        review_id: str,
        status: ReviewStatus,
        *,
        reviewer: str,
        notes: str = "",
    ) -> dict[str, Any]:
        validate_review_status(status)
        item = self.get(review_id)
        previous_status = item.status
        item.status = status
        item.reviewer = reviewer
        item.reviewed_at = utc_now_iso()
        item.audit_trail.append(
            build_audit_entry(
                action="status_changed",
                status=status,
                reviewer=reviewer,
                notes=notes or "Status atualizado em modo local dry-run.",
                previous_status=previous_status,
            )
        )
        self._save(item)
        return {
            "updated": True,
            "dry_run": True,
            "external_operations": [],
            "review": item.to_dict(),
            "approval_effect": "local_status_only_no_external_action",
        }

    def next_review_id(self) -> str:
        ids = [item.review_id for item in self._load_all()]
        numbers = [
            int(match.group(1))
            for review_id in ids
            if (match := re.fullmatch(r"REV-(\d+)", review_id))
        ]
        return f"REV-{(max(numbers) + 1 if numbers else 1):03d}"

    def _load_all(self) -> list[ReviewItem]:
        self._ensure_structure()
        items: list[ReviewItem] = []
        for path in sorted(self.base_dir.glob("*.json")):
            items.append(ReviewItem.from_dict(json.loads(path.read_text(encoding="utf-8"))))
        items.sort(key=lambda item: (item.created_at, item.review_id))
        return items

    def _save(self, item: ReviewItem) -> None:
        self._ensure_structure()
        self._path(item.review_id).write_text(
            json.dumps(item.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _path(self, review_id: str) -> Path:
        return self.base_dir / f"{_safe_filename(review_id)}.json"

    def _ensure_structure(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)


def _safe_filename(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.strip().lower())
    normalized = "".join(char for char in text if not unicodedata.combining(char))
    safe = re.sub(r"[^a-z0-9_.-]+", "-", normalized).strip(".-")
    return safe or "review"
