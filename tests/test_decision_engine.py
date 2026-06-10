import unittest

from src.domain.decision_engine import decide
from src.domain.models import TaskPayload


class DecisionEngineTests(unittest.TestCase):
    def test_request_correction_when_evidence_is_missing(self) -> None:
        task = TaskPayload.from_dict(
            {
                "task_id": "1",
                "task_name": "Validar vistoria",
                "obra": "Obra Teste",
                "departamento_responsavel": "Engenharia",
                "etapa_obra": "Campo",
                "status_agente": "Pronto para análise",
                "impacto_prazo": "Baixo",
                "impacto_financeiro": "Baixo",
                "impacto_cliente": "Baixo",
                "evidencia_obrigatoria": ["Foto"],
                "attachments": [],
                "comments": [],
            }
        )

        result = decide(task)

        self.assertEqual(result.decision, "request_correction")
        self.assertEqual(result.risk_level, "medium")
        self.assertIn("Foto", result.missing_evidence)

    def test_escalate_when_financial_impact_is_high(self) -> None:
        task = TaskPayload.from_dict(
            {
                "task_id": "2",
                "task_name": "Aprovar compra crítica",
                "obra": "Obra Teste",
                "departamento_responsavel": "Compras",
                "etapa_obra": "Compras",
                "status_agente": "Pronto para análise",
                "impacto_financeiro": "Alto",
                "evidencia_obrigatoria": [],
                "attachments": [],
                "comments": [],
            }
        )

        result = decide(task)

        self.assertEqual(result.decision, "escalate_management")
        self.assertEqual(result.risk_level, "high")
        self.assertTrue(result.requires_human_review)

    def test_approve_when_evidence_is_complete_and_risk_is_low(self) -> None:
        task = TaskPayload.from_dict(
            {
                "task_id": "3",
                "task_name": "Conferir checklist",
                "obra": "Obra Teste",
                "departamento_responsavel": "Qualidade",
                "etapa_obra": "Qualidade",
                "status_agente": "Pronto para análise",
                "impacto_prazo": "Baixo",
                "impacto_financeiro": "Baixo",
                "impacto_cliente": "Baixo",
                "evidencia_obrigatoria": ["Checklist"],
                "attachments": [{"name": "checklist_qualidade.pdf"}],
                "comments": [],
            }
        )

        result = decide(task)

        self.assertEqual(result.decision, "approved")
        self.assertFalse(result.requires_human_review)

    def test_client_approval_generates_serializable_next_task(self) -> None:
        task = TaskPayload.from_dict(
            {
                "task_id": "4",
                "task_name": "Validar mudança de escopo",
                "obra": "Obra Teste",
                "departamento_responsavel": "Atendimento",
                "etapa_obra": "Cliente",
                "status_agente": "Pronto para análise",
                "precisa_aprovacao_cliente": True,
                "attachments": [],
                "comments": [],
            }
        )

        result = decide(task)
        serialized = result.to_dict()

        self.assertEqual(result.decision, "ask_client")
        self.assertTrue(result.requires_human_review)
        self.assertEqual(serialized["next_tasks"][0]["department"], "Atendimento")
        self.assertIn("revisão humana", result.asana_comment.lower())

    def test_next_department_creates_next_task_without_human_review(self) -> None:
        task = TaskPayload.from_dict(
            {
                "task_id": "5",
                "task_name": "Liberar medição",
                "obra": "Obra Teste",
                "departamento_responsavel": "Engenharia",
                "etapa_obra": "Medição",
                "status_agente": "Pronto para análise",
                "impacto_prazo": "Baixo",
                "impacto_financeiro": "Baixo",
                "impacto_cliente": "Baixo",
                "proximo_departamento": "Financeiro",
                "attachments": [{"name": "medicao_final.pdf"}],
                "comments": [],
            }
        )

        result = decide(task)

        self.assertEqual(result.decision, "create_next_tasks")
        self.assertFalse(result.requires_human_review)
        self.assertEqual(result.next_tasks[0].department, "Financeiro")

    def test_blocked_task_requires_human_review(self) -> None:
        task = TaskPayload.from_dict(
            {
                "task_id": "6",
                "task_name": "Resolver impedimento de campo",
                "obra": "Obra Teste",
                "departamento_responsavel": "Engenharia",
                "etapa_obra": "Campo",
                "status_agente": "Bloqueado",
                "impacto_prazo": "Baixo",
                "impacto_financeiro": "Baixo",
                "impacto_cliente": "Baixo",
                "attachments": [],
                "comments": [],
            }
        )

        result = decide(task)

        self.assertEqual(result.decision, "blocked")
        self.assertTrue(result.requires_human_review)
        self.assertIn("revisão humana", result.asana_comment.lower())


if __name__ == "__main__":
    unittest.main()
