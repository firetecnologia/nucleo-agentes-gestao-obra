import json
import unittest

from src.api import create_app


def _task_payload() -> dict:
    return {
        "task_id": "task-api-1",
        "task_name": "Validar frente de obra",
        "obra": "Obra Teste",
        "departamento_responsavel": "Engenharia",
        "etapa_obra": "Campo",
        "status_agente": "Pronto para analise",
        "impacto_prazo": "Baixo",
        "impacto_financeiro": "Baixo",
        "impacto_cliente": "Baixo",
        "evidencia_obrigatoria": [],
        "attachments": [],
        "comments": [],
        "dependencies": [],
        "custom_notes": {},
    }


def _report_payload() -> dict:
    return {
        "report_type": "weekly_management",
        "payload": {
            "obra": "Obra Teste",
            "periodo": {"inicio": "2026-06-01", "fim": "2026-06-07"},
            "items": [
                {
                    "task_id": "1",
                    "task_name": "Campo aprovado",
                    "department": "Engenharia",
                    "decision": "approved",
                    "risk_level": "low",
                }
            ],
        },
    }


def _dashboard_payload() -> dict:
    return {
        "obra": "Obra Teste",
        "cliente": "Cliente Exemplo",
        "periodo": {"inicio": "2026-06-01", "fim": "2026-06-30"},
        "analyses": [],
        "events": [],
        "reports": [],
    }


class ApiRoutesTests(unittest.TestCase):
    def test_health_route_returns_registered_routes(self) -> None:
        app = create_app()

        response = app.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["status"], "ok")
        self.assertTrue(response.body["dry_run"])
        self.assertEqual(response.body["external_operations"], [])
        self.assertGreaterEqual(len(response.body["routes"]), 4)
        json.dumps(response.to_dict())

    def test_analyze_task_route(self) -> None:
        response = create_app().post("/analyze-task", _task_payload())

        self.assertEqual(response.status_code, 200)
        self.assertIn(response.body["decision"], {"approved", "create_next_tasks", "monitor"})
        self.assertTrue(response.body["dry_run"])
        self.assertEqual(response.body["external_operations"], [])
        json.dumps(response.to_dict())

    def test_process_event_route(self) -> None:
        payload = {
            "event_id": "evt-api",
            "event_type": "task_ready_for_agent_review",
            "task_id": "task-api-1",
            "task_payload": _task_payload(),
        }

        response = create_app().post("/process-event", payload)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.body["processed"])
        self.assertTrue(response.body["dry_run"])
        self.assertEqual(response.body["external_operations"], [])

    def test_generate_report_route(self) -> None:
        response = create_app().post("/generate-report", _report_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["report_type"], "weekly_management")
        self.assertTrue(response.body["dry_run"])
        self.assertEqual(response.body["external_operations"], [])

    def test_generate_dashboard_route(self) -> None:
        response = create_app().post("/generate-dashboard", _dashboard_payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body["obra"], "Obra Teste")
        self.assertTrue(response.body["dry_run"])
        self.assertEqual(response.body["external_operations"], [])

    def test_unknown_route_returns_json_error(self) -> None:
        response = create_app().post("/rota-inexistente", {})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "not_found")
        self.assertTrue(response.body["dry_run"])


if __name__ == "__main__":
    unittest.main()
