import json
import tempfile
import unittest
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.dashboard import build_dashboard_from_dict
from src.domain.models import TaskPayload
from src.reports import build_report_from_dict
from src.review import ReviewQueue
from src.simulation import SimulationRunner
from src.templates import MINIMUM_PHASES, build_nucleo_work_template, build_project_seed


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class NucleoWorkTemplateTests(unittest.TestCase):
    def test_template_contains_required_phases_and_operational_sections(self) -> None:
        template = build_nucleo_work_template()
        phase_names = [phase["nome"] for phase in template["etapas"]]

        self.assertTrue(template["dry_run"])
        self.assertEqual(template["external_operations"], [])
        self.assertEqual(template["data_policy"]["uses_real_client_data"], False)
        for phase in MINIMUM_PHASES:
            self.assertIn(phase, phase_names)
        self.assertIn("weekly_report_model", template)
        self.assertIn("dashboard_model", template)
        self.assertGreaterEqual(len(template["departamentos"]), 8)

    def test_each_phase_has_tasks_evidence_owners_risks_and_approval_points(self) -> None:
        template = build_nucleo_work_template()

        for phase in template["etapas"]:
            self.assertTrue(phase["tarefas_padrao"], phase["nome"])
            for task in phase["tarefas_padrao"]:
                self.assertTrue(task["required_evidence"], task)
                self.assertTrue(task["suggested_owner"], task)
                self.assertTrue(task["common_risks"], task)
                self.assertIn("needs_management_approval", task)
                self.assertIn("needs_client_approval", task)
                self.assertTrue(task["dry_run"])
                self.assertEqual(task["external_operations"], [])

        self.assertTrue(template["approval_points"]["gestao"])
        self.assertTrue(template["approval_points"]["cliente"])

    def test_seed_feeds_analysis_simulation_report_dashboard_and_review_queue(self) -> None:
        seed = build_project_seed()

        self.assertTrue(seed["dry_run"])
        self.assertEqual(seed["external_operations"], [])
        analyses = []
        orchestrator = OrchestratorAgent()
        for payload in seed["task_payloads"]:
            task = TaskPayload.from_dict(payload)
            decision = orchestrator.analyze(task).to_dict()
            analyses.append(decision)
            self.assertIn("decision", decision)
            self.assertIn("risk_level", decision)

        with tempfile.TemporaryDirectory() as temp_dir:
            simulation_output = SimulationRunner(history_dir=temp_dir).run(seed["simulation_scenario"])
            queue = ReviewQueue(temp_dir)
            review_outputs = [queue.add_decision(decision) for decision in seed["review_decisions"]]

        report_output = build_report_from_dict(seed["report_input"], "weekly_management").to_dict()
        dashboard_output = build_dashboard_from_dict(seed["dashboard_input"]).to_dict()

        self.assertGreaterEqual(len(analyses), 5)
        self.assertTrue(simulation_output["dry_run"])
        self.assertEqual(simulation_output["external_operations"], [])
        self.assertTrue(report_output["dry_run"])
        self.assertEqual(report_output["external_operations"], [])
        self.assertTrue(dashboard_output["dry_run"])
        self.assertEqual(dashboard_output["external_operations"], [])
        self.assertTrue(any(review_outputs))

    def test_samples_are_safe_json_contracts(self) -> None:
        template_sample = _load_json("samples/nucleo_obra_piloto_template.json")
        seed_sample = _load_json("samples/nucleo_obra_piloto_seed.json")

        self.assertTrue(template_sample["dry_run"])
        self.assertEqual(template_sample["external_operations"], [])
        self.assertFalse(template_sample["data_policy"]["uses_real_client_data"])
        self.assertGreaterEqual(len(template_sample["etapas"]), len(MINIMUM_PHASES))

        self.assertTrue(seed_sample["dry_run"])
        self.assertEqual(seed_sample["external_operations"], [])
        self.assertTrue(seed_sample["task_payloads"])
        TaskPayload.from_dict(seed_sample["task_payloads"][0])
        json.dumps(seed_sample)


def _load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
