import json
import unittest

from src.integrations.asana_mapping import map_decision_to_asana_operations


def _decision(**overrides):
    payload = {
        "task_id": "task-1",
        "task_name": "Validar etapa",
        "obra": "Obra Teste",
        "department": "Engenharia",
        "decision": "request_correction",
        "risk_level": "medium",
        "missing_evidence": ["Foto"],
        "requires_human_review": True,
    }
    payload.update(overrides)
    return payload


class AsanaMappingTests(unittest.TestCase):
    def test_maps_request_correction_to_planned_internal_comment(self) -> None:
        operations = map_decision_to_asana_operations(_decision())
        operation_names = [operation["operation"] for operation in operations]

        self.assertIn("planned_internal_comment", operation_names)
        self.assertIn("planned_field_update", operation_names)
        self.assertTrue(all(operation["dry_run"] for operation in operations))
        self.assertTrue(all(not operation["external_call"] for operation in operations))
        json.dumps(operations)

    def test_maps_ask_client_to_internal_review_task(self) -> None:
        operations = map_decision_to_asana_operations(
            _decision(decision="ask_client", department="Atendimento")
        )

        self.assertIn("planned_internal_task", [operation["operation"] for operation in operations])
        self.assertIn("planned_human_review", [operation["operation"] for operation in operations])
        encoded = json.dumps(operations).lower()
        self.assertNotIn("send_client_message", encoded)
        self.assertNotIn("whatsapp", encoded)
        self.assertNotIn("email", encoded)

    def test_maps_escalate_management_to_management_task(self) -> None:
        operations = map_decision_to_asana_operations(
            _decision(decision="escalate_management", department="Financeiro", risk_level="high")
        )
        management_tasks = [
            operation
            for operation in operations
            if operation["operation"] == "planned_internal_task"
            and operation["payload"]["department"] == "Gestao"
        ]

        self.assertEqual(len(management_tasks), 1)
        self.assertIn("planned_human_review", [operation["operation"] for operation in operations])

    def test_maps_create_next_tasks_to_next_department_tasks(self) -> None:
        operations = map_decision_to_asana_operations(
            _decision(
                decision="create_next_tasks",
                next_tasks=[
                    {
                        "name": "Planejar proxima frente",
                        "department": "Planejamento",
                        "description": "Preparar cronograma da proxima frente.",
                    }
                ],
                requires_human_review=False,
            )
        )
        planned_tasks = [operation for operation in operations if operation["operation"] == "planned_internal_task"]

        self.assertEqual(planned_tasks[0]["payload"]["department"], "Planejamento")


if __name__ == "__main__":
    unittest.main()
