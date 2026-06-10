import json
import unittest

from src.agents.client_service_agent import ClientServiceAgent
from src.agents.engineering_agent import EngineeringAgent
from src.agents.finance_agent import FinanceAgent
from src.agents.orchestrator import OrchestratorAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.projects_agent import ProjectsAgent
from src.agents.purchasing_agent import PurchasingAgent
from src.agents.quality_agent import QualityAgent
from src.domain.models import TaskPayload
from src.events.event_processor import EventProcessor


def _task_payload(**overrides):
    payload = {
        "task_id": "task-fase-4",
        "task_name": "Validar etapa da obra",
        "obra": "Obra Teste",
        "departamento_responsavel": "Engenharia",
        "etapa_obra": "Execucao",
        "status_agente": "Pronto para analise",
        "prioridade": "Baixa",
        "impacto_prazo": "Baixo",
        "impacto_financeiro": "Baixo",
        "impacto_cliente": "Baixo",
        "precisa_aprovacao_gestao": False,
        "precisa_aprovacao_cliente": False,
        "evidencia_obrigatoria": [],
        "attachments": [],
        "comments": [],
        "description": "Payload de teste da fase 4.",
        "dependencies": [],
        "custom_notes": {},
    }
    payload.update(overrides)
    return payload


class SpecialistAgentsTests(unittest.TestCase):
    def test_orchestrator_routes_engineering_department_to_specialist(self) -> None:
        task = TaskPayload.from_dict(
            _task_payload(
                departamento_responsavel="Engenharia",
                evidencia_obrigatoria=["Foto"],
            )
        )

        decision = OrchestratorAgent().analyze(task)

        self.assertEqual(decision.specialist_agent, "EngineeringAgent")
        self.assertIsNotNone(decision.specialist_analysis)
        self.assertEqual(decision.specialist_analysis["department"], "Engenharia")
        json.dumps(decision.to_dict())

    def test_engineering_without_photo_requests_correction(self) -> None:
        task = TaskPayload.from_dict(
            _task_payload(
                departamento_responsavel="Engenharia",
                evidencia_obrigatoria=["Foto"],
                attachments=[],
            )
        )

        decision = OrchestratorAgent().analyze(task)

        self.assertEqual(decision.decision, "request_correction")
        self.assertIn("Foto", decision.missing_evidence)
        self.assertTrue(decision.requires_human_review)

    def test_finance_with_medium_financial_impact_escalates(self) -> None:
        task = TaskPayload.from_dict(
            _task_payload(
                departamento_responsavel="Financeiro",
                impacto_financeiro="Medio",
            )
        )

        decision = OrchestratorAgent().analyze(task)

        self.assertEqual(decision.specialist_agent, "FinanceAgent")
        self.assertEqual(decision.decision, "escalate_management")
        self.assertTrue(decision.requires_human_review)

    def test_client_service_approval_requires_human_review_without_external_send(self) -> None:
        task = TaskPayload.from_dict(
            _task_payload(
                departamento_responsavel="Atendimento",
                precisa_aprovacao_cliente=True,
                impacto_cliente="Alto",
            )
        )

        decision = OrchestratorAgent().analyze(task)
        serialized = decision.to_dict()

        self.assertEqual(decision.specialist_agent, "ClientServiceAgent")
        self.assertEqual(decision.decision, "ask_client")
        self.assertTrue(decision.requires_human_review)
        self.assertNotIn("send_client_message", json.dumps(serialized))
        self.assertIn("Nenhuma mensagem", " ".join(decision.recommended_actions))

    def test_projects_with_critical_conflict_blocks_execution(self) -> None:
        task = TaskPayload.from_dict(
            _task_payload(
                departamento_responsavel="Projetos",
                impacto_prazo="Alto",
                description="Conflito critico entre projeto estrutural e executivo incompleto.",
            )
        )

        decision = OrchestratorAgent().analyze(task)

        self.assertEqual(decision.specialist_agent, "ProjectsAgent")
        self.assertEqual(decision.decision, "blocked")
        self.assertEqual(decision.next_tasks, [])

    def test_quality_without_checklist_prevents_automatic_approval(self) -> None:
        task = TaskPayload.from_dict(
            _task_payload(
                departamento_responsavel="Qualidade",
                evidencia_obrigatoria=["Checklist"],
                attachments=[],
            )
        )

        decision = OrchestratorAgent().analyze(task)

        self.assertEqual(decision.specialist_agent, "QualityAgent")
        self.assertEqual(decision.decision, "request_correction")
        self.assertNotEqual(decision.decision, "approved")
        self.assertTrue(decision.requires_human_review)

    def test_processed_event_includes_specialist_analysis(self) -> None:
        processor = EventProcessor()
        result = processor.process(
            {
                "event_id": "evt-specialist",
                "event_type": "task_ready_for_agent_review",
                "task_id": "task-fase-4",
                "task_payload": _task_payload(
                    departamento_responsavel="Engenharia",
                    evidencia_obrigatoria=["Foto"],
                ),
            }
        )
        serialized = result.to_dict()

        self.assertTrue(result.processed)
        self.assertEqual(result.specialist_agent, "EngineeringAgent")
        self.assertEqual(serialized["specialist_agent"], "EngineeringAgent")
        self.assertEqual(serialized["specialist_analysis"]["agent_name"], "EngineeringAgent")
        self.assertTrue(all(operation["dry_run"] for operation in result.planned_operations))

    def test_specialists_do_not_execute_external_actions(self) -> None:
        task = TaskPayload.from_dict(_task_payload())
        specialists = [
            PlanningAgent(),
            ProjectsAgent(),
            EngineeringAgent(),
            PurchasingAgent(),
            FinanceAgent(),
            ClientServiceAgent(),
            QualityAgent(),
        ]

        for specialist in specialists:
            with self.subTest(agent=specialist.agent_name):
                analysis = specialist.analyze(task).to_dict()
                self.assertNotIn("planned_operations", analysis)
                self.assertNotIn("send_client_message", json.dumps(analysis))


if __name__ == "__main__":
    unittest.main()
