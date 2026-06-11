import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from src.agents.orchestrator import OrchestratorAgent
from src.dashboard import build_dashboard_from_dict
from src.domain.models import TaskPayload
from src.events.event_processor import EventProcessor
from src.integrations.asana_mapping import map_decision_to_asana_operations
from src.reports import build_report_from_dict
from src.review import ReviewQueue
from src.simulation import SimulationRunner, load_scenario


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


class SecurityDryRunTests(unittest.TestCase):
    def test_sensitive_outputs_remain_dry_run_without_external_operations(self) -> None:
        task = TaskPayload.from_dict(_load_json("sample_task_payload.json"))
        decision_output = OrchestratorAgent().analyze(task).to_dict()
        decision_output["dry_run"] = True
        decision_output["external_operations"] = []

        event_output = EventProcessor().process(_load_json("samples/asana_event_client_decision.json")).to_dict()
        report_output = build_report_from_dict(
            _load_json("samples/report_input_weekly.json"),
            "weekly_management",
        ).to_dict()
        dashboard_output = build_dashboard_from_dict(_load_json("samples/dashboard_input_obra.json")).to_dict()

        scenario = load_scenario(PROJECT_ROOT / "samples" / "obra_piloto_scenario.json")
        with tempfile.TemporaryDirectory() as temp_dir:
            simulation_output = SimulationRunner(history_dir=temp_dir).run(scenario)
            queue = ReviewQueue(temp_dir)
            review = queue.add_decision(
                {
                    "obra": "Obra Segura",
                    "task_id": "task-review",
                    "decision": "ask_client",
                    "risk_level": "medium",
                    "requires_human_review": True,
                },
                review_id="REV-SEC",
            )
            review_update = queue.update_status("REV-SEC", "approved", reviewer="Gestao")

        mapping_output = {
            "dry_run": True,
            "external_operations": [],
            "planned_operations": map_decision_to_asana_operations(
                {
                    "task_id": "task-client",
                    "task_name": "Decisao de cliente",
                    "obra": "Obra Segura",
                    "department": "Atendimento",
                    "decision": "ask_client",
                    "risk_level": "medium",
                    "requires_human_review": True,
                }
            ),
        }

        for output in [
            decision_output,
            event_output,
            report_output,
            dashboard_output,
            simulation_output,
            review,
            review_update,
            mapping_output,
        ]:
            self.assert_is_safe_dry_run(output)

    def test_client_communication_remains_draft_only(self) -> None:
        output = build_report_from_dict(
            _load_json("samples/report_input_weekly.json"),
            "client_draft",
        ).to_dict()
        encoded = json.dumps(output).lower()

        self.assertTrue(output["dry_run"])
        self.assertEqual(output["external_operations"], [])
        self.assertTrue(output["client_draft"]["requires_human_review"])
        self.assertEqual(output["client_draft"]["external_delivery"], "draft_only_no_external_send")
        self.assertNotIn("send_client_message", encoded)
        self.assertNotIn("whatsapp", encoded)
        self.assertNotIn("email", encoded)

    def assert_is_safe_dry_run(self, output: Any) -> None:
        self.assertIsInstance(output, dict)
        self.assertTrue(output.get("dry_run"), output)
        self.assertEqual(output.get("external_operations", []), [])
        self.assert_no_active_external_operation(output)

    def assert_no_active_external_operation(self, value: Any) -> None:
        if isinstance(value, dict):
            if "planned_operations" in value:
                self.assertIsInstance(value["planned_operations"], list)
                for operation in value["planned_operations"]:
                    self.assertTrue(operation.get("dry_run"), operation)
                    self.assertFalse(operation.get("external_call", False), operation)
                    self.assertFalse(operation.get("real_action", False), operation)
            for nested in value.values():
                self.assert_no_active_external_operation(nested)
        elif isinstance(value, list):
            for item in value:
                self.assert_no_active_external_operation(item)


if __name__ == "__main__":
    unittest.main()
