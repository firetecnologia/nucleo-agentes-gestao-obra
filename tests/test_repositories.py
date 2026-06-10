import json
import tempfile
import unittest
from pathlib import Path

from src.storage import RecordRepository


class RecordRepositoryTests(unittest.TestCase):
    def test_repository_saves_and_queries_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = RecordRepository(temp_dir)
            repository.save(
                {
                    "id": "analysis-1",
                    "obra": "Obra Teste",
                    "record_type": "analysis",
                    "payload": {"decision": "request_correction"},
                }
            )
            repository.save(
                {
                    "id": "event-1",
                    "obra": "Obra Teste",
                    "record_type": "event",
                    "payload": {"event_type": "task_ready_for_agent_review"},
                }
            )

            result = repository.query(obra="Obra Teste", record_type="analysis")

            self.assertTrue(result["dry_run"])
            self.assertEqual(result["external_operations"], [])
            self.assertEqual(result["count"], 1)
            self.assertEqual(result["records"][0]["record_type"], "analysis")
            json.dumps(result)

    def test_query_from_dict_uses_storage_query(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = RecordRepository(temp_dir)
            repository.save(
                {
                    "id": "dashboard-1",
                    "obra": "Obra Piloto Nucleo",
                    "record_type": "dashboard",
                    "payload": {"health_status": "attention"},
                }
            )

            result = repository.query_from_dict(
                {"obra": "Obra Piloto Nucleo", "record_type": "dashboard"}
            )

            self.assertEqual(result["count"], 1)
            self.assertEqual(result["records"][0]["payload"]["health_status"], "attention")

    def test_gitignore_keeps_local_data_out_of_repo(self) -> None:
        gitignore = Path(".gitignore").read_text(encoding="utf-8")

        self.assertIn("local_data/", gitignore)


if __name__ == "__main__":
    unittest.main()
