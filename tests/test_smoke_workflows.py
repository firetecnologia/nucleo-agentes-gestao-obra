import json
import tempfile
import unittest
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.dashboard import build_dashboard_from_dict
from src.domain.models import TaskPayload
from src.events.event_processor import EventProcessor
from src.integrations.asana_mapping import map_decision_to_asana_operations
from src.reports import build_report_from_dict
from src.review import ReviewQueue
from src.simulation import SimulationRunner, load_scenario
from src.web import create_web_app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


class SmokeWorkflowTests(unittest.TestCase):
    def test_smoke_analyze_task_flow(self) -> None:
        task = TaskPayload.from_dict(_load_json("sample_task_payload.json"))
        output = OrchestratorAgent().analyze(task).to_dict()
        output["dry_run"] = True

        self.assertTrue(output["dry_run"])
        self.assertIn(output["decision"], {"approved", "request_correction", "escalate_management", "ask_client", "create_next_tasks", "blocked", "monitor"})
        json.dumps(output)

    def test_smoke_process_event_flow(self) -> None:
        output = EventProcessor().process(_load_json("samples/asana_event_task_ready.json")).to_dict()

        self.assertTrue(output["dry_run"])
        self.assertTrue(output["processed"])
        self.assertTrue(all(operation["dry_run"] for operation in output["planned_operations"]))
        json.dumps(output)

    def test_smoke_generate_weekly_report_flow(self) -> None:
        output = build_report_from_dict(
            _load_json("samples/report_input_weekly.json"),
            "weekly_management",
        ).to_dict()

        self.assertTrue(output["dry_run"])
        self.assertEqual(output["external_operations"], [])
        self.assertEqual(output["report_type"], "weekly_management")
        json.dumps(output)

    def test_smoke_generate_dashboard_flow(self) -> None:
        output = build_dashboard_from_dict(_load_json("samples/dashboard_input_obra.json")).to_dict()

        self.assertTrue(output["dry_run"])
        self.assertEqual(output["external_operations"], [])
        self.assertIn("metrics", output)
        json.dumps(output)

    def test_smoke_simulation_flow(self) -> None:
        scenario = load_scenario(PROJECT_ROOT / "samples" / "obra_piloto_scenario.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            output = SimulationRunner(history_dir=temp_dir).run(scenario)

        self.assertTrue(output["dry_run"])
        self.assertEqual(output["external_operations"], [])
        self.assertGreaterEqual(len(output["saved_records"]), 5)
        json.dumps(output)

    def test_smoke_review_queue_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue = ReviewQueue(temp_dir)
            review = queue.add_decision(
                {
                    "obra": "Obra Smoke",
                    "task_id": "task-smoke",
                    "decision": "escalate_management",
                    "risk_level": "high",
                    "requires_human_review": True,
                    "impacto_financeiro": "Alto",
                }
            )
            listed = queue.list_reviews()

        self.assertIsNotNone(review)
        self.assertTrue(review["dry_run"])
        self.assertEqual(review["external_operations"], [])
        self.assertEqual(listed["count"], 1)

    def test_smoke_web_interface_flow(self) -> None:
        response = create_web_app().get("/dashboard")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.dry_run)
        self.assertEqual(response.external_operations, [])
        self.assertIn("Dashboard executivo", response.body)

    def test_smoke_asana_mapping_sandbox_flow(self) -> None:
        operations = map_decision_to_asana_operations(
            {
                "task_id": "task-map",
                "task_name": "Validar evidencia",
                "obra": "Obra Smoke",
                "department": "Engenharia",
                "decision": "request_correction",
                "risk_level": "medium",
                "missing_evidence": ["Foto"],
                "requires_human_review": True,
            }
        )

        self.assertTrue(operations)
        self.assertTrue(all(operation["dry_run"] for operation in operations))
        self.assertTrue(all(not operation["external_call"] for operation in operations))
        json.dumps(operations)


if __name__ == "__main__":
    unittest.main()
