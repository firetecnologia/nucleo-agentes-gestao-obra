import tempfile
import unittest

from src.review import ReviewQueue


def _decision(**overrides):
    payload = {
        "obra": "Obra Teste",
        "task_id": "task-1",
        "decision": "escalate_management",
        "risk_level": "high",
        "requires_human_review": True,
        "impacto_financeiro": "Alto",
    }
    payload.update(overrides)
    return payload


class ReviewQueueTests(unittest.TestCase):
    def test_creates_review_item_when_human_review_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue = ReviewQueue(temp_dir)
            created = queue.add_decision(_decision())
            listed = queue.list_reviews()

        self.assertIsNotNone(created)
        self.assertEqual(created["review_id"], "REV-001")
        self.assertEqual(created["status"], "pending")
        self.assertEqual(listed["count"], 1)
        self.assertEqual(listed["external_operations"], [])

    def test_does_not_create_review_for_approved_low_risk(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue = ReviewQueue(temp_dir)
            created = queue.add_decision(
                _decision(
                    decision="approved",
                    risk_level="low",
                    requires_human_review=False,
                    impacto_financeiro="Baixo",
                )
            )
            listed = queue.list_reviews()

        self.assertIsNone(created)
        self.assertEqual(listed["count"], 0)

    def test_updates_status_locally_and_records_audit_trail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue = ReviewQueue(temp_dir)
            queue.add_decision(_decision(), review_id="REV-010")
            output = queue.update_status(
                "REV-010",
                "approved",
                reviewer="Gestao",
                notes="Aprovado somente na fila local.",
            )
            stored = queue.get("REV-010").to_dict()

        self.assertTrue(output["updated"])
        self.assertTrue(output["dry_run"])
        self.assertEqual(output["external_operations"], [])
        self.assertEqual(output["approval_effect"], "local_status_only_no_external_action")
        self.assertEqual(stored["status"], "approved")
        self.assertEqual(stored["reviewer"], "Gestao")
        self.assertGreaterEqual(len(stored["audit_trail"]), 2)
        self.assertEqual(stored["audit_trail"][-1]["previous_status"], "pending")

    def test_rejects_invalid_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue = ReviewQueue(temp_dir)
            queue.add_decision(_decision(), review_id="REV-011")
            with self.assertRaises(ValueError):
                queue.update_status(
                    "REV-011",
                    "enviado",  # type: ignore[arg-type]
                    reviewer="Gestao",
                )

    def test_no_external_operation_is_created_for_client_decision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue = ReviewQueue(temp_dir)
            created = queue.add_decision(
                _decision(decision="ask_client", task_id="task-client", risk_level="medium")
            )
            output = queue.update_status(created["review_id"], "changes_requested", reviewer="Atendimento")

        encoded = str(output).lower()
        self.assertEqual(output["external_operations"], [])
        self.assertNotIn("send_client_message", encoded)
        self.assertNotIn("whatsapp", encoded)
        self.assertNotIn("email", encoded)


if __name__ == "__main__":
    unittest.main()
