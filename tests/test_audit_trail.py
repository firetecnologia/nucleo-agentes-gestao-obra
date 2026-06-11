import unittest

from src.review.audit_trail import append_audit_entry, build_audit_entry


class AuditTrailTests(unittest.TestCase):
    def test_builds_dry_run_audit_entry(self) -> None:
        entry = build_audit_entry(
            action="status_changed",
            status="approved",
            reviewer="Gestao",
            previous_status="pending",
        )

        self.assertEqual(entry["action"], "status_changed")
        self.assertEqual(entry["status"], "approved")
        self.assertEqual(entry["reviewer"], "Gestao")
        self.assertEqual(entry["previous_status"], "pending")
        self.assertTrue(entry["dry_run"])
        self.assertEqual(entry["external_operations"], [])

    def test_appends_audit_entry_without_external_operation(self) -> None:
        review = {"review_id": "REV-001", "audit_trail": []}
        updated = append_audit_entry(
            review,
            build_audit_entry(action="status_changed", status="rejected", reviewer="Gestao"),
        )

        self.assertEqual(len(updated["audit_trail"]), 1)
        self.assertTrue(updated["audit_trail"][0]["dry_run"])
        self.assertEqual(updated["audit_trail"][0]["external_operations"], [])


if __name__ == "__main__":
    unittest.main()
