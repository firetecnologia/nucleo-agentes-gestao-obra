import json
import unittest

from src.dashboard import build_dashboard_from_dict


class DashboardBuilderTests(unittest.TestCase):
    def test_generates_dashboard_for_work(self) -> None:
        dashboard = build_dashboard_from_dict(
            {
                "obra": "Obra Teste",
                "cliente": "Cliente Exemplo",
                "periodo": {"inicio": "2026-06-01", "fim": "2026-06-30"},
                "analyses": [
                    {
                        "task_id": "1",
                        "task_name": "Campo aprovado",
                        "department": "Engenharia",
                        "decision": "approved",
                        "risk_level": "low",
                    },
                    {
                        "task_id": "2",
                        "task_name": "Projeto pendente",
                        "department": "Projetos",
                        "decision": "request_correction",
                        "risk_level": "medium",
                        "requires_human_review": True,
                    },
                    {
                        "task_id": "3",
                        "task_name": "Medicao financeira",
                        "department": "Financeiro",
                        "decision": "escalate_management",
                        "risk_level": "high",
                        "requires_human_review": True,
                        "impacto_financeiro": "Alto",
                    },
                ],
                "events": [],
                "reports": [
                    {
                        "department_bottlenecks": {"Financeiro": 2},
                        "recommended_actions": [
                            "Validar impacto financeiro em reuniao de gestao."
                        ],
                    }
                ],
            }
        )
        serialized = dashboard.to_dict()

        self.assertEqual(serialized["obra"], "Obra Teste")
        self.assertEqual(serialized["cliente"], "Cliente Exemplo")
        self.assertEqual(serialized["health_status"], "at_risk")
        self.assertEqual(serialized["metrics"]["total_tasks_analyzed"], 3)
        self.assertEqual(serialized["metrics"]["financial_impact_count"], 1)
        self.assertIn("Financeiro", serialized["department_summary"])
        self.assertGreaterEqual(len(serialized["decision_history"]), 3)
        self.assertGreaterEqual(len(serialized["active_risks"]), 2)
        self.assertGreaterEqual(len(serialized["pending_decisions"]), 2)
        self.assertTrue(serialized["dry_run"])
        self.assertEqual(serialized["external_operations"], [])
        json.dumps(serialized)

    def test_dashboard_output_has_no_external_operation(self) -> None:
        dashboard = build_dashboard_from_dict(
            {
                "obra": "Obra Segura",
                "cliente": "Cliente Exemplo",
                "periodo": {},
                "analyses": [],
                "events": [],
                "reports": [],
            }
        )
        serialized = dashboard.to_dict()
        encoded = json.dumps(serialized).lower()

        self.assertTrue(serialized["dry_run"])
        self.assertEqual(serialized["external_operations"], [])
        self.assertNotIn("send_client_message", encoded)
        self.assertNotIn("email", encoded)
        self.assertNotIn("whatsapp", encoded)


if __name__ == "__main__":
    unittest.main()
