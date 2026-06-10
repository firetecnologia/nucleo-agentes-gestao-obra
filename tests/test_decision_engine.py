from src.domain.decision_engine import decide
from src.domain.models import TaskPayload


def test_request_correction_when_evidence_is_missing():
    task = TaskPayload.from_dict(
        {
            "task_id": "1",
            "task_name": "Validar vistoria",
            "obra": "Obra Teste",
            "departamento_responsavel": "Engenharia",
            "etapa_obra": "Campo",
            "status_agente": "Pronto para analise",
            "impacto_prazo": "Baixo",
            "impacto_financeiro": "Baixo",
            "impacto_cliente": "Baixo",
            "evidencia_obrigatoria": ["Foto"],
            "attachments": [],
            "comments": [],
        }
    )

    result = decide(task)

    assert result.decision == "request_correction"
    assert result.risk_level == "medium"
    assert "Foto" in result.missing_evidence


def test_escalate_when_financial_impact_is_high():
    task = TaskPayload.from_dict(
        {
            "task_id": "2",
            "task_name": "Aprovar compra critica",
            "obra": "Obra Teste",
            "departamento_responsavel": "Compras",
            "etapa_obra": "Compras",
            "status_agente": "Pronto para analise",
            "impacto_financeiro": "Alto",
            "evidencia_obrigatoria": [],
            "attachments": [],
            "comments": [],
        }
    )

    result = decide(task)

    assert result.decision == "escalate_management"
    assert result.risk_level == "high"
    assert result.requires_human_review is True


def test_approve_when_evidence_is_complete_and_risk_is_low():
    task = TaskPayload.from_dict(
        {
            "task_id": "3",
            "task_name": "Conferir checklist",
            "obra": "Obra Teste",
            "departamento_responsavel": "Qualidade",
            "etapa_obra": "Qualidade",
            "status_agente": "Pronto para analise",
            "impacto_prazo": "Baixo",
            "impacto_financeiro": "Baixo",
            "impacto_cliente": "Baixo",
            "evidencia_obrigatoria": ["Checklist"],
            "attachments": [{"name": "checklist_qualidade.pdf"}],
            "comments": [],
        }
    )

    result = decide(task)

    assert result.decision == "approved"
    assert result.requires_human_review is False
