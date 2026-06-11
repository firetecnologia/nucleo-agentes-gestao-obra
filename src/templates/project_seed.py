from __future__ import annotations

from copy import deepcopy
from typing import Any

from .nucleo_work_template import build_nucleo_work_template


def build_project_seed(template: dict[str, Any] | None = None) -> dict[str, Any]:
    template_data = deepcopy(template or build_nucleo_work_template())
    task_payloads = _task_payloads(template_data)
    analyses = _analysis_contracts()
    events = _events(task_payloads)
    report_input = {
        "obra": template_data["obra"]["nome"],
        "periodo": template_data["obra"]["periodo_estimado"],
        "items": _report_items(analyses),
    }
    weekly_report_stub = {
        "report_type": "weekly_management",
        "obra": template_data["obra"]["nome"],
        "health_status": "attention",
        "period": template_data["obra"]["periodo_estimado"],
        "recommended_actions": [
            "Priorizar evidencias pendentes antes de liberar novas frentes.",
            "Gestao deve revisar impacto financeiro antes de qualquer aprovacao.",
        ],
        "dry_run": True,
        "external_operations": [],
    }

    return {
        "seed_id": "nucleo-377-obra-piloto-seed-v1",
        "template_id": template_data["template_id"],
        "dry_run": True,
        "external_operations": [],
        "obra": template_data["obra"],
        "cliente": template_data["cliente"],
        "task_payloads": task_payloads,
        "simulation_scenario": {
            "scenario": "nucleo_obra_piloto_template_seed",
            "obra": template_data["obra"]["nome"],
            "cliente": template_data["cliente"]["nome"],
            "periodo": template_data["obra"]["periodo_estimado"],
            "tasks": task_payloads[:3],
            "events": events,
        },
        "report_input": report_input,
        "dashboard_input": {
            "obra": template_data["obra"]["nome"],
            "cliente": template_data["cliente"]["nome"],
            "periodo": template_data["obra"]["periodo_estimado"],
            "analyses": analyses,
            "events": events,
            "reports": [weekly_report_stub],
        },
        "review_decisions": [
            {
                "obra": template_data["obra"]["nome"],
                "task_id": "NUC-FIN-001",
                "task_name": "Validar medicao da semana",
                "department": "Financeiro",
                "decision": "escalate_management",
                "risk_level": "high",
                "impacto_financeiro": "Alto",
                "requires_human_review": True,
                "dry_run": True,
                "external_operations": [],
            },
            {
                "obra": template_data["obra"]["nome"],
                "task_id": "NUC-ATE-001",
                "task_name": "Preparar termo de entrega assistida",
                "department": "Atendimento",
                "decision": "ask_client",
                "risk_level": "medium",
                "requires_human_review": True,
                "dry_run": True,
                "external_operations": [],
            },
        ],
    }


def _task_payloads(template_data: dict[str, Any]) -> list[dict[str, Any]]:
    obra = template_data["obra"]["nome"]
    return [
        {
            "task_id": "NUC-PLAN-001",
            "task_name": "Levantar escopo e restricoes",
            "obra": obra,
            "departamento_responsavel": "Planejamento",
            "etapa_obra": "Diagnostico inicial",
            "status_agente": "Pronto para analise",
            "prioridade": "Media",
            "assignee": "Planejamento",
            "due_on": "2026-06-05",
            "impacto_prazo": "Baixo",
            "impacto_financeiro": "Baixo",
            "impacto_cliente": "Baixo",
            "proximo_departamento": "Projetos",
            "precisa_aprovacao_gestao": False,
            "precisa_aprovacao_cliente": False,
            "evidencia_obrigatoria": ["Checklist", "Foto"],
            "attachments": [
                {"name": "checklist_diagnostico.pdf", "type": "application/pdf"},
                {"name": "foto_ambiente_inicial.jpg", "type": "image/jpeg"},
            ],
            "comments": [
                {
                    "author": "Planejamento",
                    "text": "Checklist e foto inicial anexados para avaliacao dry-run.",
                }
            ],
            "description": "Diagnostico sintetico para a obra piloto.",
            "dependencies": [],
            "custom_notes": {"template_seed": True},
        },
        {
            "task_id": "NUC-PROJ-001",
            "task_name": "Compatibilizar projetos executivos",
            "obra": obra,
            "departamento_responsavel": "Projetos",
            "etapa_obra": "Projetos e compatibilizacao",
            "status_agente": "Pronto para analise",
            "prioridade": "Alta",
            "assignee": "Projetos",
            "due_on": "2026-06-12",
            "impacto_prazo": "Medio",
            "impacto_financeiro": "Baixo",
            "impacto_cliente": "Medio",
            "precisa_aprovacao_gestao": False,
            "precisa_aprovacao_cliente": False,
            "evidencia_obrigatoria": ["Projeto", "Checklist"],
            "attachments": [{"name": "checklist_compatibilizacao.pdf", "type": "application/pdf"}],
            "comments": [
                {
                    "author": "Projetos",
                    "text": "Checklist recebido; arquivo de projeto executivo ainda pendente.",
                }
            ],
            "description": "Projeto executivo deve ser anexado antes de liberar campo.",
            "dependencies": [],
            "custom_notes": {"template_seed": True},
        },
        {
            "task_id": "NUC-ENG-001",
            "task_name": "Registrar execucao de campo",
            "obra": obra,
            "departamento_responsavel": "Engenharia",
            "etapa_obra": "Execucao acompanhada",
            "status_agente": "Pronto para analise",
            "prioridade": "Alta",
            "assignee": "Engenharia",
            "due_on": "2026-06-20",
            "impacto_prazo": "Medio",
            "impacto_financeiro": "Baixo",
            "impacto_cliente": "Baixo",
            "precisa_aprovacao_gestao": False,
            "precisa_aprovacao_cliente": False,
            "evidencia_obrigatoria": ["Foto", "Diario de obra"],
            "attachments": [{"name": "foto_execucao_campo.jpg", "type": "image/jpeg"}],
            "comments": [
                {
                    "author": "Engenharia",
                    "text": "Foto anexada; diario de obra sera complementado.",
                }
            ],
            "description": "Evidencia de execucao parcial para demonstracao.",
            "dependencies": [],
            "custom_notes": {"template_seed": True},
        },
        {
            "task_id": "NUC-FIN-001",
            "task_name": "Validar medicao da semana",
            "obra": obra,
            "departamento_responsavel": "Financeiro",
            "etapa_obra": "Medicoes",
            "status_agente": "Pronto para analise",
            "prioridade": "Alta",
            "assignee": "Financeiro",
            "due_on": "2026-06-24",
            "impacto_prazo": "Baixo",
            "impacto_financeiro": "Alto",
            "impacto_cliente": "Baixo",
            "precisa_aprovacao_gestao": True,
            "precisa_aprovacao_cliente": False,
            "evidencia_obrigatoria": ["Medicao", "Nota fiscal"],
            "attachments": [{"name": "medicao_semana_03.pdf", "type": "application/pdf"}],
            "comments": [
                {
                    "author": "Financeiro",
                    "text": "Medicao anexada; nota fiscal ainda aguardando validacao.",
                }
            ],
            "description": "Impacto financeiro alto exige revisao humana.",
            "dependencies": [],
            "custom_notes": {"template_seed": True},
        },
        {
            "task_id": "NUC-ATE-001",
            "task_name": "Preparar termo de entrega assistida",
            "obra": obra,
            "departamento_responsavel": "Atendimento",
            "etapa_obra": "Entrega",
            "status_agente": "Pronto para analise",
            "prioridade": "Media",
            "assignee": "Atendimento",
            "due_on": "2026-07-01",
            "impacto_prazo": "Baixo",
            "impacto_financeiro": "Baixo",
            "impacto_cliente": "Alto",
            "precisa_aprovacao_gestao": False,
            "precisa_aprovacao_cliente": True,
            "evidencia_obrigatoria": ["Checklist"],
            "attachments": [{"name": "checklist_entrega_assistida.pdf", "type": "application/pdf"}],
            "comments": [
                {
                    "author": "Atendimento",
                    "text": "Rascunho deve ficar interno ate revisao humana.",
                }
            ],
            "description": "Nenhuma mensagem ao cliente deve ser enviada automaticamente.",
            "dependencies": [],
            "custom_notes": {"template_seed": True},
        },
    ]


def _events(task_payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    finance_payload = deepcopy(task_payloads[3])
    client_payload = deepcopy(task_payloads[4])
    return [
        {
            "event_id": "NUC-EVT-FIN-001",
            "event_type": "financial_impact_detected",
            "task_id": finance_payload["task_id"],
            "occurred_at": "2026-06-24T12:00:00Z",
            "source": "asana_webhook_stub",
            "dry_run": True,
            "metadata": {"reason": "medicao com impacto financeiro alto no seed"},
            "task_payload": finance_payload,
        },
        {
            "event_id": "NUC-EVT-CLI-001",
            "event_type": "client_decision_required",
            "task_id": client_payload["task_id"],
            "occurred_at": "2026-07-01T09:00:00Z",
            "source": "asana_webhook_stub",
            "dry_run": True,
            "metadata": {"reason": "aprovacao de entrega deve virar rascunho interno"},
            "task_payload": client_payload,
        },
    ]


def _analysis_contracts() -> list[dict[str, Any]]:
    return [
        _analysis("NUC-PLAN-001", "Levantar escopo e restricoes", "Planejamento", "create_next_tasks", "low", False),
        _analysis("NUC-PROJ-001", "Compatibilizar projetos executivos", "Projetos", "request_correction", "medium", True),
        _analysis("NUC-ENG-001", "Registrar execucao de campo", "Engenharia", "request_correction", "medium", True),
        _analysis("NUC-FIN-001", "Validar medicao da semana", "Financeiro", "escalate_management", "high", True),
        _analysis("NUC-ATE-001", "Preparar termo de entrega assistida", "Atendimento", "ask_client", "medium", True),
    ]


def _analysis(
    task_id: str,
    task_name: str,
    department: str,
    decision: str,
    risk_level: str,
    requires_human_review: bool,
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "task_name": task_name,
        "department": department,
        "decision": decision,
        "risk_level": risk_level,
        "requires_human_review": requires_human_review,
        "recommended_actions": [
            "Manter fluxo em dry-run e registrar proximo passo no historico da obra."
        ],
        "impacto_financeiro": "Alto" if department == "Financeiro" else "Baixo",
        "created_at": "2026-06-24T10:00:00Z",
        "dry_run": True,
        "external_operations": [],
    }


def _report_items(analyses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "task_id": item["task_id"],
            "task_name": item["task_name"],
            "department": item["department"],
            "decision": item["decision"],
            "risk_level": item["risk_level"],
            "requires_human_review": item["requires_human_review"],
            "recommended_actions": list(item["recommended_actions"]),
            "missing_evidence": ["Projeto"] if item["task_id"] == "NUC-PROJ-001" else [],
            "planned_operations": [{"operation": "dry_run_plan", "dry_run": True}],
            "impacto_prazo": "Medio" if item["risk_level"] == "medium" else "Baixo",
            "impacto_financeiro": item["impacto_financeiro"],
            "impacto_cliente": "Alto" if item["department"] == "Atendimento" else "Baixo",
        }
        for item in analyses
    ]
