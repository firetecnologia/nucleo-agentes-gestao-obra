import unittest

from src.dashboard.decision_history import build_decision_history
from src.dashboard.metrics import calculate_metrics
from src.dashboard.work_health import calculate_work_health


class MetricsTests(unittest.TestCase):
    def test_calculates_core_metrics_and_rates(self) -> None:
        analyses = [
            {
                "task_id": "1",
                "task_name": "Aprovada",
                "department": "Engenharia",
                "decision": "approved",
                "risk_level": "low",
            },
            {
                "task_id": "2",
                "task_name": "Corrigir",
                "department": "Projetos",
                "decision": "request_correction",
                "risk_level": "medium",
                "requires_human_review": True,
            },
            {
                "task_id": "3",
                "task_name": "Cliente",
                "department": "Atendimento",
                "decision": "ask_client",
                "risk_level": "high",
                "requires_human_review": True,
                "impacto_financeiro": "Alto",
            },
        ]
        history = build_decision_history(analyses=analyses)

        metrics = calculate_metrics(history, analyses=analyses)

        self.assertEqual(metrics.total_tasks_analyzed, 3)
        self.assertEqual(metrics.approved_count, 1)
        self.assertEqual(metrics.correction_count, 1)
        self.assertEqual(metrics.human_review_count, 2)
        self.assertEqual(metrics.medium_risk_count, 1)
        self.assertEqual(metrics.high_risk_count, 1)
        self.assertEqual(metrics.client_decision_count, 1)
        self.assertEqual(metrics.financial_impact_count, 1)
        self.assertAlmostEqual(metrics.approval_rate, 0.3333)
        self.assertAlmostEqual(metrics.rework_pending_rate, 0.6667)
        self.assertLess(metrics.health_index, 100)

    def test_consolidates_department_bottlenecks_from_reports(self) -> None:
        analyses = [
            {
                "task_id": "1",
                "task_name": "Financeiro",
                "department": "Financeiro",
                "decision": "escalate_management",
                "risk_level": "high",
                "requires_human_review": True,
            }
        ]
        reports = [{"department_bottlenecks": {"Financeiro": 3}}]
        history = build_decision_history(analyses=analyses)

        metrics = calculate_metrics(history, analyses=analyses, reports=reports)

        self.assertEqual(metrics.department_bottlenecks["Financeiro"], 3)

    def test_classifies_work_health(self) -> None:
        empty_metrics = calculate_metrics([])
        self.assertEqual(calculate_work_health(empty_metrics, []), "attention")

        approved_history = build_decision_history(
            analyses=[
                {
                    "task_id": "1",
                    "task_name": "Aprovada",
                    "department": "Engenharia",
                    "decision": "approved",
                    "risk_level": "low",
                }
            ]
        )
        self.assertEqual(
            calculate_work_health(calculate_metrics(approved_history), approved_history),
            "on_track",
        )

        critical_history = build_decision_history(
            analyses=[
                {
                    "task_id": "2",
                    "task_name": "Bloqueada",
                    "department": "Compras",
                    "decision": "blocked",
                    "risk_level": "high",
                    "requires_human_review": True,
                }
            ]
        )
        self.assertEqual(
            calculate_work_health(calculate_metrics(critical_history), critical_history),
            "critical",
        )


if __name__ == "__main__":
    unittest.main()
