import json
import tempfile
import unittest
from pathlib import Path

from src.simulation import SimulationRunner, load_scenario


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SimulationRunnerTests(unittest.TestCase):
    def test_runs_obra_piloto_end_to_end_in_dry_run(self) -> None:
        scenario = load_scenario(PROJECT_ROOT / "samples" / "obra_piloto_scenario.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            output = SimulationRunner(history_dir=temp_dir).run(scenario)

        self.assertTrue(output["dry_run"])
        self.assertEqual(output["external_operations"], [])
        self.assertEqual(output["obra"], "Nucleo 377 - Obra Piloto")

        self.assertEqual(output["analyses"][0]["decision"], "request_correction")
        self.assertIn("Diario de obra", output["analyses"][0]["missing_evidence"])
        self.assertEqual(output["events_processed"][0]["decision"], "escalate_management")
        self.assertTrue(output["events_processed"][0]["requires_human_review"])

        self.assertEqual(output["weekly_report"]["report_type"], "weekly_management")
        self.assertTrue(output["weekly_report"]["dry_run"])
        self.assertEqual(output["weekly_report"]["external_operations"], [])

        self.assertEqual(output["dashboard"]["obra"], "Nucleo 377 - Obra Piloto")
        self.assertGreaterEqual(output["dashboard"]["metrics"]["financial_impact_count"], 1)
        self.assertTrue(output["dashboard"]["dry_run"])
        self.assertEqual(output["dashboard"]["external_operations"], [])

        self.assertGreaterEqual(len(output["saved_records"]), 5)
        self.assertEqual(output["storage_query"]["count"], len(output["saved_records"]))
        self.assertTrue(output["storage_query"]["dry_run"])
        self.assertEqual(output["storage_query"]["external_operations"], [])

        self.assertGreaterEqual(len(output["planned_operations"]), 4)
        self.assertTrue(all(operation["dry_run"] for operation in output["planned_operations"]))
        self.assertTrue(
            all(not operation.get("external_call", False) for operation in output["planned_operations"])
        )

        self.assertTrue(all(route["status_code"] == 200 for route in output["web_preview"]["routes"]))
        json.dumps(output)


if __name__ == "__main__":
    unittest.main()
