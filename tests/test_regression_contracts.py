import json
import unittest
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.dashboard import build_dashboard_from_dict
from src.domain.models import TaskPayload
from src.events.event_processor import EventProcessor
from src.reports import build_report_from_dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


class RegressionContractTests(unittest.TestCase):
    def test_agent_decision_contract(self) -> None:
        task = TaskPayload.from_dict(_load_json("sample_task_payload.json"))
        output = OrchestratorAgent().analyze(task).to_dict()

        self.assert_contract_keys(
            output,
            {
                "decision",
                "risk_level",
                "analysis",
                "asana_comment",
                "validated_evidence",
                "missing_evidence",
                "recommended_actions",
                "next_tasks",
                "requires_human_review",
            },
        )
        self.assertIsInstance(output["next_tasks"], list)
        json.dumps(output)

    def test_event_processing_contract(self) -> None:
        output = EventProcessor().process(_load_json("samples/asana_event_task_ready.json")).to_dict()

        self.assert_contract_keys(
            output,
            {
                "event_type",
                "processed",
                "dry_run",
                "decision",
                "planned_operations",
                "log_entry",
                "requires_human_review",
            },
        )
        self.assertTrue(output["dry_run"])
        self.assertIsInstance(output["planned_operations"], list)
        json.dumps(output)

    def test_weekly_report_contract(self) -> None:
        output = build_report_from_dict(
            _load_json("samples/report_input_weekly.json"),
            "weekly_management",
        ).to_dict()

        self.assert_contract_keys(
            output,
            {
                "report_type",
                "obra",
                "health_status",
                "summary",
                "period",
                "risks",
                "pending_decisions",
                "recommended_actions",
                "requires_human_review",
                "dry_run",
                "external_operations",
            },
        )
        self.assertEqual(output["report_type"], "weekly_management")
        self.assertTrue(output["dry_run"])
        json.dumps(output)

    def test_dashboard_contract(self) -> None:
        output = build_dashboard_from_dict(_load_json("samples/dashboard_input_obra.json")).to_dict()

        self.assert_contract_keys(
            output,
            {
                "obra",
                "cliente",
                "health_status",
                "metrics",
                "decision_history",
                "active_risks",
                "pending_decisions",
                "department_summary",
                "recommended_management_actions",
                "period",
                "dry_run",
                "external_operations",
            },
        )
        self.assertIn("total_tasks_analyzed", output["metrics"])
        self.assertTrue(output["dry_run"])
        json.dumps(output)

    def assert_contract_keys(self, output: dict, expected_keys: set[str]) -> None:
        missing = expected_keys.difference(output.keys())
        self.assertFalse(missing, f"Contrato JSON sem chave(s): {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
