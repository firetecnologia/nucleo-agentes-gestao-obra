import json
import unittest

from src.reports import build_report_from_dict, classify_health_status
from src.reports.report_models import ReportItem


def _base_input(items):
    return {
        "obra": "Obra Teste",
        "periodo": {"inicio": "2026-06-10", "fim": "2026-06-17"},
        "items": items,
    }


def _item(**overrides):
    payload = {
        "task_id": "task-1",
        "task_name": "Validar etapa",
        "department": "Engenharia",
        "decision": "approved",
        "risk_level": "low",
        "requires_human_review": False,
        "specialist_agent": "EngineeringAgent",
        "recommended_actions": [],
        "missing_evidence": [],
        "planned_operations": [],
        "impacto_prazo": "Baixo",
        "impacto_financeiro": "Baixo",
        "impacto_cliente": "Baixo",
    }
    payload.update(overrides)
    return payload


class ReportBuilderTests(unittest.TestCase):
    def test_build_internal_daily_report(self) -> None:
        report = build_report_from_dict(
            _base_input(
                [
                    _item(task_id="1", task_name="Checklist aprovado", decision="approved"),
                    _item(
                        task_id="2",
                        task_name="Complementar foto",
                        decision="request_correction",
                        risk_level="medium",
                        requires_human_review=True,
                        missing_evidence=["Foto"],
                    ),
                    _item(
                        task_id="3",
                        task_name="Compra pendente",
                        department="Compras",
                        decision="blocked",
                        risk_level="high",
                        requires_human_review=True,
                    ),
                ]
            ),
            "internal_daily",
        )
        serialized = report.to_dict()

        self.assertEqual(serialized["report_type"], "internal_daily")
        self.assertEqual(len(serialized["tasks_analyzed"]), 3)
        self.assertEqual(len(serialized["approved_tasks"]), 1)
        self.assertEqual(len(serialized["correction_requested_tasks"]), 1)
        self.assertEqual(len(serialized["blocked_tasks"]), 1)
        self.assertIn("Compras", serialized["department_pending"])
        self.assertTrue(serialized["requires_human_review"])
        json.dumps(serialized)

    def test_build_weekly_management_report(self) -> None:
        report = build_report_from_dict(
            _base_input(
                [
                    _item(task_id="1", task_name="Campo liberado", decision="approved"),
                    _item(
                        task_id="2",
                        task_name="Revisar projeto",
                        department="Projetos",
                        decision="request_correction",
                        risk_level="high",
                        requires_human_review=True,
                        impacto_prazo="Alto",
                    ),
                    _item(
                        task_id="3",
                        task_name="Revisar medicao",
                        department="Financeiro",
                        decision="escalate_management",
                        risk_level="high",
                        requires_human_review=True,
                        impacto_financeiro="Alto",
                    ),
                ]
            ),
            "weekly_management",
        )
        serialized = report.to_dict()

        self.assertEqual(serialized["report_type"], "weekly_management")
        self.assertEqual(serialized["health_status"], "at_risk")
        self.assertIn("Projetos", serialized["department_bottlenecks"])
        self.assertIn("Financeiro", serialized["department_bottlenecks"])
        self.assertGreaterEqual(len(serialized["pending_decisions"]), 2)
        self.assertGreaterEqual(len(serialized["deadline_impacts"]), 1)
        self.assertGreaterEqual(len(serialized["financial_impacts"]), 1)
        json.dumps(serialized)

    def test_classify_health_status_rules(self) -> None:
        self.assertEqual(classify_health_status([ReportItem.from_dict(_item())]), "on_track")
        self.assertEqual(
            classify_health_status(
                [
                    ReportItem.from_dict(
                        _item(
                            decision="request_correction",
                            risk_level="medium",
                            requires_human_review=True,
                        )
                    )
                ]
            ),
            "attention",
        )
        self.assertEqual(
            classify_health_status(
                [
                    ReportItem.from_dict(_item(task_id="1", risk_level="high")),
                    ReportItem.from_dict(_item(task_id="2", risk_level="high")),
                ]
            ),
            "at_risk",
        )
        self.assertEqual(
            classify_health_status(
                [ReportItem.from_dict(_item(decision="blocked", risk_level="high"))]
            ),
            "critical",
        )

    def test_report_output_is_json_serializable(self) -> None:
        report = build_report_from_dict(
            _base_input([_item(task_id="1", task_name="Tarefa aprovada")]),
            "weekly_management",
        )

        encoded = json.dumps(report.to_dict())

        self.assertIn("weekly_management", encoded)


if __name__ == "__main__":
    unittest.main()
