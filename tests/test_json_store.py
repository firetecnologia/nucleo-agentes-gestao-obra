import json
import tempfile
import unittest
from pathlib import Path

from src.storage.json_store import JsonStore
from src.storage.storage_models import StorageRecord


class JsonStoreTests(unittest.TestCase):
    def test_save_record_locally_and_keeps_json_serializable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonStore(temp_dir)
            record = StorageRecord.from_dict(
                {
                    "id": "registro-1",
                    "obra": "Obra Teste",
                    "record_type": "analysis",
                    "created_at": "2026-06-10T09:00:00Z",
                    "payload": {"decision": "approved"},
                }
            )

            result = store.save_record(record)

            self.assertTrue(result["saved"])
            self.assertTrue(result["dry_run"])
            self.assertEqual(result["external_operations"], [])
            self.assertTrue(Path(result["path"]).exists())
            json.dumps(result)

    def test_query_by_obra_and_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonStore(temp_dir)
            store.save_record(
                StorageRecord.from_dict(
                    {
                        "id": "a",
                        "obra": "Obra Piloto Nucleo",
                        "record_type": "analysis",
                        "payload": {},
                    }
                )
            )
            store.save_record(
                StorageRecord.from_dict(
                    {
                        "id": "b",
                        "obra": "Outra Obra",
                        "record_type": "report",
                        "payload": {},
                    }
                )
            )

            records = store.query_records(obra="obra piloto nucleo", record_type="analysis")

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].id, "a")

    def test_creates_expected_local_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonStore(temp_dir)

            store.ensure_structure()

            for directory in ["analyses", "events", "reports", "dashboards", "decision_history"]:
                self.assertTrue((Path(temp_dir) / directory).is_dir())


if __name__ == "__main__":
    unittest.main()
