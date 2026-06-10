import json
import unittest

from src.reports import build_report_from_dict


class ClientReportDraftTests(unittest.TestCase):
    def test_client_draft_requires_human_review(self) -> None:
        report = build_report_from_dict(
            {
                "obra": "Obra Teste",
                "periodo": {"inicio": "2026-06-10", "fim": "2026-06-17"},
                "items": [
                    {
                        "task_id": "task-client",
                        "task_name": "Preparar decisao do cliente",
                        "department": "Atendimento",
                        "decision": "ask_client",
                        "risk_level": "medium",
                        "requires_human_review": True,
                        "impacto_cliente": "Alto",
                        "recommended_actions": [
                            "Preparar rascunho interno para revisao humana."
                        ],
                        "missing_evidence": [],
                        "planned_operations": [],
                    }
                ],
            },
            "client_draft",
        )
        serialized = report.to_dict()

        self.assertEqual(serialized["report_type"], "client_draft")
        self.assertTrue(serialized["requires_human_review"])
        self.assertTrue(serialized["client_draft"]["requires_human_review"])
        self.assertEqual(
            serialized["client_draft"]["external_delivery"],
            "draft_only_no_external_send",
        )
        self.assertIn("controle", serialized["client_draft"]["control_phrase"].lower())
        json.dumps(serialized)

    def test_client_draft_does_not_create_external_send_operation(self) -> None:
        report = build_report_from_dict(
            {
                "obra": "Obra Teste",
                "periodo": {"inicio": "2026-06-10", "fim": "2026-06-17"},
                "items": [
                    {
                        "task_id": "task-client",
                        "task_name": "Aprovar ajuste",
                        "department": "Atendimento",
                        "decision": "ask_client",
                        "risk_level": "medium",
                        "requires_human_review": True,
                        "planned_operations": [
                            {"operation": "create_task", "dry_run": True}
                        ],
                    }
                ],
            },
            "client_draft",
        )
        serialized = report.to_dict()
        encoded = json.dumps(serialized)

        self.assertEqual(serialized["external_operations"], [])
        self.assertNotIn("send_client_message", encoded)
        self.assertNotIn("email", encoded.lower())
        self.assertNotIn("whatsapp", encoded.lower())

    def test_client_draft_uses_safe_language(self) -> None:
        report = build_report_from_dict(
            {
                "obra": "Obra Teste",
                "periodo": {"inicio": "2026-06-10", "fim": "2026-06-17"},
                "items": [
                    {
                        "task_id": "task-risk",
                        "task_name": "Conflito interno com atraso critico",
                        "department": "Projetos",
                        "decision": "request_correction",
                        "risk_level": "high",
                        "requires_human_review": True,
                        "impacto_prazo": "Alto",
                        "recommended_actions": [
                            "Nao expor conflito interno ao cliente."
                        ],
                    }
                ],
            },
            "client_draft",
        )
        encoded = json.dumps(report.to_dict()).lower()

        self.assertNotIn("conflito interno", encoded)
        self.assertNotIn("desorganiz", encoded)
        self.assertNotIn("alarmista", encoded)
        self.assertIn("previsibilidade", encoded)


if __name__ == "__main__":
    unittest.main()
