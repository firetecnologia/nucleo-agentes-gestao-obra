import unittest

from src.review.approval_rules import (
    create_review_item_from_decision,
    requires_human_review,
    review_reasons,
)


def _decision(**overrides):
    payload = {
        "obra": "Obra Teste",
        "task_id": "task-1",
        "decision": "approved",
        "risk_level": "low",
        "requires_human_review": False,
        "impacto_financeiro": "Baixo",
    }
    payload.update(overrides)
    return payload


class ApprovalRulesTests(unittest.TestCase):
    def test_requires_review_when_decision_is_sensitive(self) -> None:
        self.assertTrue(requires_human_review(_decision(decision="blocked")))
        self.assertTrue(requires_human_review(_decision(decision="ask_client")))
        self.assertTrue(requires_human_review(_decision(decision="escalate_management")))

    def test_requires_review_for_financial_impact_and_risk(self) -> None:
        self.assertTrue(requires_human_review(_decision(impacto_financeiro="Medio")))
        self.assertTrue(requires_human_review(_decision(impacto_financeiro="Alto")))
        self.assertTrue(requires_human_review(_decision(impacto_financeiro="Critico")))
        self.assertTrue(requires_human_review(_decision(risk_level="high")))
        self.assertTrue(requires_human_review(_decision(risk_level="critical")))

    def test_client_decision_always_requires_review(self) -> None:
        reasons = review_reasons(_decision(decision="ask_client"))

        self.assertTrue(any("cliente" in reason.lower() for reason in reasons))

    def test_approved_low_risk_does_not_create_review(self) -> None:
        decision = _decision()

        self.assertFalse(requires_human_review(decision))
        self.assertIsNone(create_review_item_from_decision(decision, review_id="REV-001"))

    def test_creates_structured_review_item(self) -> None:
        item = create_review_item_from_decision(
            _decision(decision="escalate_management", risk_level="high"),
            review_id="REV-001",
        )

        self.assertIsNotNone(item)
        serialized = item.to_dict()
        self.assertEqual(serialized["review_id"], "REV-001")
        self.assertEqual(serialized["status"], "pending")
        self.assertTrue(serialized["audit_trail"])
        self.assertEqual(serialized["external_operations"], [])


if __name__ == "__main__":
    unittest.main()
