from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable
import unicodedata

from .storage_models import RecordType, StorageRecord


RECORD_TYPE_DIRECTORIES: dict[str, str] = {
    "analysis": "analyses",
    "event": "events",
    "report": "reports",
    "dashboard": "dashboards",
    "decision_history": "decision_history",
}


class JsonStore:
    def __init__(self, base_dir: str | Path = "local_data") -> None:
        self.base_dir = Path(base_dir)

    def ensure_structure(self) -> None:
        for directory in RECORD_TYPE_DIRECTORIES.values():
            (self.base_dir / directory).mkdir(parents=True, exist_ok=True)

    def save_record(self, record: StorageRecord) -> dict:
        self.ensure_structure()
        path = self._record_path(record)
        path.write_text(
            json.dumps(record.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return {
            "saved": True,
            "dry_run": True,
            "path": str(path),
            "record": record.to_dict(),
            "external_operations": [],
        }

    def list_records(self, record_type: RecordType | None = None) -> list[StorageRecord]:
        self.ensure_structure()
        paths = self._iter_record_paths(record_type)
        records: list[StorageRecord] = []
        for path in paths:
            records.append(StorageRecord.from_dict(json.loads(path.read_text(encoding="utf-8"))))
        records.sort(key=lambda record: (record.created_at, record.id))
        return records

    def query_records(
        self,
        *,
        obra: str | None = None,
        record_type: RecordType | None = None,
    ) -> list[StorageRecord]:
        obra_key = _normalize(obra)
        records = self.list_records(record_type=record_type)
        if not obra_key:
            return records
        return [record for record in records if _normalize(record.obra) == obra_key]

    def _iter_record_paths(self, record_type: RecordType | None) -> Iterable[Path]:
        if record_type:
            directories = [RECORD_TYPE_DIRECTORIES[record_type]]
        else:
            directories = list(RECORD_TYPE_DIRECTORIES.values())

        for directory in directories:
            yield from sorted((self.base_dir / directory).glob("*.json"))

    def _record_path(self, record: StorageRecord) -> Path:
        directory = RECORD_TYPE_DIRECTORIES[record.record_type]
        safe_id = _safe_filename(record.id)
        return self.base_dir / directory / f"{safe_id}.json"


def _safe_filename(value: str) -> str:
    normalized = _normalize(value).replace(" ", "-")
    safe = re.sub(r"[^a-z0-9_.-]+", "-", normalized).strip(".-")
    return safe or "registro"


def _normalize(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", (value or "").strip().lower())
    return "".join(char for char in text if not unicodedata.combining(char))
