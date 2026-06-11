import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.export import (
    export_client_draft_from_dict,
    export_dashboard_from_dict,
    export_simulation_summary,
    export_weekly_report_from_dict,
)
from src.simulation import SimulationRunner, load_scenario


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class HtmlExporterTests(unittest.TestCase):
    def test_weekly_report_html_export_is_local_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            result = export_weekly_report_from_dict(
                _load_json("samples/report_input_weekly.json"),
                output_dir=output_dir,
            )

            html = Path(result["path"]).read_text(encoding="utf-8")

        self.assert_export_result(result, "weekly_report")
        self.assertIn("Relatorio semanal executivo", html)
        self.assertIn("DOCUMENTO INTERNO", html)
        self.assertIn("dry_run=true", html)

    def test_dashboard_html_export_includes_decision_history(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            result = export_dashboard_from_dict(
                _load_json("samples/dashboard_input_obra.json"),
                output_dir=output_dir,
            )
            html = Path(result["path"]).read_text(encoding="utf-8")

        self.assert_export_result(result, "dashboard")
        self.assertIn("Dashboard executivo", html)
        self.assertIn("Historico de decisoes", html)
        self.assertIn("Gargalos", html)

    def test_client_draft_html_requires_review_and_sanitizes_terms(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            result = export_client_draft_from_dict(
                _load_json("samples/report_input_weekly.json"),
                output_dir=output_dir,
            )
            html = Path(result["path"]).read_text(encoding="utf-8").lower()

        self.assert_export_result(result, "client_draft")
        self.assertIn("revisao humana obrigatoria", html)
        self.assertNotIn("conflito interno", html)
        self.assertNotIn("desorganizacao", html)
        self.assertNotIn("erro interno", html)
        self.assertNotIn("falha interna", html)
        self.assertNotIn("atraso critico", html)
        self.assertNotIn("whatsapp", html)
        self.assertNotIn("email", html)

    def test_simulation_summary_html_export(self) -> None:
        scenario = load_scenario(PROJECT_ROOT / "samples" / "obra_piloto_scenario.json")
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as output_dir:
            simulation_output = SimulationRunner(history_dir=temp_dir).run(scenario)
            result = export_simulation_summary(simulation_output, output_dir=output_dir)
            html = Path(result["path"]).read_text(encoding="utf-8")

        self.assert_export_result(result, "simulation_summary")
        self.assertIn("Resumo da simulacao", html)
        self.assertIn("Simulacao dry-run", html)

    def test_cli_exports_dashboard_html(self) -> None:
        with tempfile.TemporaryDirectory() as output_dir:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.workflows.export_html",
                    "--type",
                    "dashboard",
                    "--input",
                    str(PROJECT_ROOT / "samples" / "dashboard_input_obra.json"),
                    "--output-dir",
                    output_dir,
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            output = json.loads(completed.stdout)
            html_path = Path(output["path"])

            self.assertTrue(html_path.exists())

        self.assert_export_result(output, "dashboard")

    def assert_export_result(self, result: dict, export_type: str) -> None:
        self.assertEqual(result["export_type"], export_type)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["external_operations"], [])
        self.assertTrue(result["path"].endswith(".html"))
        self.assertGreater(result["bytes"], 0)


def _load_json(relative_path: str) -> dict:
    return json.loads((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
