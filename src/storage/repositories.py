from __future__ import annotations

from pathlib import Path
from typing import Any

from .json_store import JsonStore
from .storage_models import RecordType, StorageRecord, StorageQuery


class RecordRepository:
    def __init__(self, base_dir: str | Path = "local_data") -> None:
        self.store = JsonStore(base_dir)

    def save(self, data: dict[str, Any] | StorageRecord) -> dict:
        record = data if isinstance(data, StorageRecord) else StorageRecord.from_dict(data)
        return self.store.save_record(record)

    def query(
        self,
        *,
        obra: str | None = None,
        record_type: RecordType | None = None,
    ) -> dict:
        records = self.store.query_records(obra=obra, record_type=record_type)
        return {
            "dry_run": True,
            "external_operations": [],
            "count": len(records),
            "records": [record.to_dict() for record in records],
        }

    def query_from_dict(self, data: dict[str, Any]) -> dict:
        query = StorageQuery.from_dict(data)
        return self.query(obra=query.obra, record_type=query.record_type)
