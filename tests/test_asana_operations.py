import json
import unittest

from src.integrations.asana_operations import (
    planned_field_update,
    planned_human_review,
    planned_internal_comment,
    planned_internal_task,
    planned_task_link,
)
from src.integrations.asana_payloads import AsanaTaskReference


class AsanaOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reference = AsanaTaskReference(
            task_id="task-1",
            task_name="Validar etapa",
            obra="Obra Teste",
            department="Engenharia",
        )

    def test_all_operations_are_safe_dry_run(self) -> None:
        operations = [
            planned_internal_comment(self.reference, "Comentario interno", reason="Teste"),
            planned_internal_task(
                self.reference,
                name="Tarefa interna",
                notes="Notas",
                department="Gestao",
                reason="Teste",
            ),
            planned_field_update(self.reference, {"status": "dry-run"}, reason="Teste"),
            planned_task_link(self.reference),
            planned_human_review(self.reference, review_reason="Teste"),
        ]

        for operation in operations:
            self.assertTrue(operation["dry_run"])
            self.assertFalse(operation["external_call"])
            self.assertFalse(operation["real_action"])
            self.assertEqual(operation["source"], "asana_sandbox_mapping")
        json.dumps(operations)

    def test_human_review_never_auto_approves(self) -> None:
        operation = planned_human_review(
            self.reference,
            review_reason="Impacto financeiro alto exige revisao.",
        )

        self.assertFalse(operation["payload"]["automatic_approval"])


if __name__ == "__main__":
    unittest.main()
