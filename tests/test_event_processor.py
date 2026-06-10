import unittest

from src.events.event_processor import EventProcessor
from src.integrations.asana_client import AsanaClient


def _base_task_payload() -> dict:
    return {
        "task_id": "task-1",
        "task_name": "Validar vistoria",
        "obra": "Obra Teste",
        "departamento_responsavel": "Engenharia",
        "etapa_obra": "Campo",
        "status_agente": "Pronto para análise",
        "prioridade": "Alta",
        "impacto_prazo": "Médio",
        "impacto_financeiro": "Baixo",
        "impacto_cliente": "Baixo",
        "precisa_aprovacao_gestao": False,
        "precisa_aprovacao_cliente": False,
        "evidencia_obrigatoria": ["Foto"],
        "attachments": [],
        "comments": [],
        "description": "Payload de teste.",
        "dependencies": [],
        "custom_notes": {},
    }


class EventProcessorTests(unittest.TestCase):
    def test_process_task_ready_for_agent_review(self) -> None:
        processor = EventProcessor()
        result = processor.process(
            {
                "event_id": "evt-1",
                "event_type": "task_ready_for_agent_review",
                "task_id": "task-1",
                "task_payload": _base_task_payload(),
            }
        )

        self.assertTrue(result.processed)
        self.assertTrue(result.dry_run)
        self.assertEqual(result.decision, "request_correction")
        self.assertEqual(result.log_entry["event_id"], "evt-1")
        self.assertGreaterEqual(len(result.planned_operations), 2)
        self.assertTrue(all(operation["dry_run"] for operation in result.planned_operations))
        self.assertEqual(result.planned_operations[0]["operation"], "fetch_task")

    def test_unknown_event_returns_controlled_error(self) -> None:
        processor = EventProcessor()
        result = processor.process(
            {
                "event_id": "evt-unknown",
                "event_type": "evento_inexistente",
                "task_id": "task-1",
            }
        )

        self.assertFalse(result.processed)
        self.assertIn("Tipo de evento desconhecido", result.error or "")
        self.assertEqual(result.planned_operations, [])
        self.assertEqual(result.log_entry["processed"], False)

    def test_client_decision_requires_human_review_and_creates_internal_task_only(self) -> None:
        payload = _base_task_payload()
        payload["precisa_aprovacao_cliente"] = True
        payload["impacto_cliente"] = "Alto"

        processor = EventProcessor()
        result = processor.process(
            {
                "event_id": "evt-client",
                "event_type": "client_decision_required",
                "task_id": "task-1",
                "task_payload": payload,
            }
        )

        operations = [operation["operation"] for operation in result.planned_operations]

        self.assertTrue(result.processed)
        self.assertEqual(result.decision, "ask_client")
        self.assertTrue(result.requires_human_review)
        self.assertIn("create_task", operations)
        self.assertNotIn("send_client_message", operations)
        self.assertTrue(all(operation["dry_run"] for operation in result.planned_operations))

    def test_financial_impact_is_escalated_without_automatic_approval(self) -> None:
        payload = _base_task_payload()
        payload["impacto_financeiro"] = "Médio"
        payload["evidencia_obrigatoria"] = []

        processor = EventProcessor()
        result = processor.process(
            {
                "event_id": "evt-finance",
                "event_type": "financial_impact_detected",
                "task_id": "task-1",
                "task_payload": payload,
            }
        )

        self.assertTrue(result.processed)
        self.assertEqual(result.decision, "escalate_management")
        self.assertTrue(result.requires_human_review)
        self.assertIn("create_task", [operation["operation"] for operation in result.planned_operations])

    def test_processor_forces_dry_run_even_if_client_is_misconfigured(self) -> None:
        unsafe_client = AsanaClient(
            dry_run=False,
            token="token-falso",
            enable_real_actions=True,
            confirm_real_action=True,
        )
        processor = EventProcessor(asana_client=unsafe_client, dry_run=False)

        result = processor.process(
            {
                "event_id": "evt-safe",
                "event_type": "task_ready_for_agent_review",
                "task_id": "task-1",
                "task_payload": _base_task_payload(),
            }
        )

        self.assertTrue(result.dry_run)
        self.assertTrue(processor.asana_client.dry_run)
        self.assertTrue(all(operation["dry_run"] for operation in result.planned_operations))

    def test_log_entry_is_structured_for_processed_event(self) -> None:
        processor = EventProcessor()
        result = processor.process(
            {
                "event_id": "evt-log",
                "event_type": "new_attachment_added",
                "task_id": "task-1",
                "task_payload": _base_task_payload(),
            }
        )

        self.assertTrue(result.log_entry["processed"])
        self.assertEqual(result.log_entry["event_type"], "new_attachment_added")
        self.assertEqual(result.log_entry["task_id"], "task-1")
        self.assertIn("logged_at", result.log_entry)
        self.assertEqual(
            result.log_entry["planned_operations_count"],
            len(result.planned_operations),
        )


if __name__ == "__main__":
    unittest.main()
