import unittest

from src.dashboard.decision_history import (
    build_decision_history,
    consolidate_pending_decisions,
    filter_history_by_decision,
    filter_history_by_department,
    filter_history_by_risk,
)


class DecisionHistoryTests(unittest.TestCase):
    def test_builds_sorted_history_from_analyses_events_and_reports(self) -> None:
        history = build_decision_history(
            analyses=[
                {
                    "task_id": "2",
                    "task_name": "Revisar projeto",
                    "department": "Projetos",
                    "decision": "request_correction",
                    "risk_level": "medium",
                    "requires_human_review": True,
                    "created_at": "2026-06-11T10:00:00Z",
                }
            ],
            events=[
                {
                    "task_id": "3",
                    "event_type": "financial_impact_detected",
                    "decision": "escalate_management",
                    "risk_level": "high",
                    "requires_human_review": True,
                    "occurred_at": "2026-06-12T08:00:00Z",
                    "task_payload": {
                        "task_name": "Revisar medicao",
                        "departamento_responsavel": "Financeiro",
                    },
                }
            ],
            reports=[
                {
                    "period": {"fim": "2026-06-13"},
                    "tasks_analyzed": [
                        {
                            "task_id": "1",
                            "task_name": "Checklist aprovado",
                            "department": "Engenharia",
                            "decision": "approved",
                            "risk_level": "low",
                        }
                    ],
                }
            ],
        )

        self.assertEqual([entry.task_id for entry in history], ["2", "3", "1"])
        self.assertEqual(history[0].source, "analysis")
        self.assertEqual(history[1].source, "event")
        self.assertEqual(history[2].source, "report")

    def test_filters_history_by_department_risk_and_decision(self) -> None:
        history = build_decision_history(
            analyses=[
                {
                    "task_id": "1",
                    "task_name": "Campo",
                    "department": "Engenharia",
                    "decision": "approved",
                    "risk_level": "low",
                },
                {
                    "task_id": "2",
                    "task_name": "Projeto",
                    "department": "Projetos",
                    "decision": "request_correction",
                    "risk_level": "high",
                    "requires_human_review": True,
                },
            ]
        )

        self.assertEqual(len(filter_history_by_department(history, "projetos")), 1)
        self.assertEqual(len(filter_history_by_risk(history, "high")), 1)
        self.assertEqual(len(filter_history_by_decision(history, "request_correction")), 1)

    def test_consolidates_pending_decisions(self) -> None:
        history = build_decision_history(
            analyses=[
                {
                    "task_id": "1",
                    "task_name": "Campo",
                    "department": "Engenharia",
                    "decision": "approved",
                    "risk_level": "low",
                },
                {
                    "task_id": "2",
                    "task_name": "Cliente",
                    "department": "Atendimento",
                    "decision": "ask_client",
                    "risk_level": "medium",
                    "requires_human_review": True,
                },
            ]
        )

        pending = consolidate_pending_decisions(history)

        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].decision, "ask_client")


if __name__ == "__main__":
    unittest.main()
