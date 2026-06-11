from __future__ import annotations

from copy import deepcopy
from typing import Any


MINIMUM_PHASES = [
    "Diagnostico inicial",
    "Planejamento",
    "Projetos e compatibilizacao",
    "Compras",
    "Execucao acompanhada",
    "Medicoes",
    "Qualidade",
    "Entrega",
    "Pos-obra",
]


def build_nucleo_work_template() -> dict[str, Any]:
    """Retorna o template operacional da obra piloto em modo seguro."""
    return deepcopy(
        {
            "template_id": "nucleo-377-obra-piloto-v1",
            "template_name": "Template operacional de obra piloto Nucleo 377",
            "dry_run": True,
            "external_operations": [],
            "data_policy": {
                "uses_real_client_data": False,
                "description": "Dados sinteticos para demonstracao interna e piloto seguro.",
            },
            "obra": {
                "nome": "Nucleo 377 - Obra Piloto Template",
                "tipo": "Reforma residencial premium",
                "localidade": "Ambiente de demonstracao",
                "periodo_estimado": {
                    "inicio": "2026-06-01",
                    "fim": "2026-09-30",
                },
            },
            "cliente": {
                "nome": "Cliente Piloto Demonstracao",
                "dados_sensiveis": False,
                "canal_externo_habilitado": False,
                "observacao": "Cliente ficticio; qualquer comunicacao permanece como rascunho.",
            },
            "departamentos": _departments(),
            "etapas": _phases(),
            "approval_points": {
                "gestao": [
                    "validar escopo e premissas antes do planejamento final",
                    "aprovar compras criticas antes de pedido",
                    "revisar impacto financeiro medio, alto ou critico",
                    "liberar entrega apenas com pendencias controladas",
                ],
                "cliente": [
                    "aprovar escopo consolidado",
                    "aprovar escolha de acabamento quando aplicavel",
                    "validar entrega assistida antes do encerramento",
                ],
            },
            "weekly_report_model": {
                "sections": [
                    "resumo executivo",
                    "saude da obra",
                    "avancos da semana",
                    "riscos e gargalos",
                    "decisoes pendentes",
                    "acoes recomendadas",
                ],
                "dry_run": True,
                "external_operations": [],
            },
            "dashboard_model": {
                "widgets": [
                    "saude da obra",
                    "tarefas por decisao",
                    "gargalos por departamento",
                    "riscos ativos",
                    "decisoes pendentes",
                    "historico de decisoes",
                ],
                "dry_run": True,
                "external_operations": [],
            },
        }
    )


def _departments() -> list[dict[str, Any]]:
    return [
        {
            "nome": "Planejamento",
            "responsavel_sugerido": "Coordenacao de planejamento",
            "foco": "prazo, caminho critico, dependencias e sequenciamento",
        },
        {
            "nome": "Projetos",
            "responsavel_sugerido": "Coordenacao de projetos",
            "foco": "compatibilizacao, versao de projeto e detalhe executivo",
        },
        {
            "nome": "Compras",
            "responsavel_sugerido": "Suprimentos",
            "foco": "cotacoes, fornecedor, lead time e aprovacao de compra",
        },
        {
            "nome": "Engenharia",
            "responsavel_sugerido": "Engenharia de obra",
            "foco": "execucao, diario de obra, evidencias e vistoria",
        },
        {
            "nome": "Financeiro",
            "responsavel_sugerido": "Financeiro",
            "foco": "medicoes, nota fiscal, previsto x realizado e desvios",
        },
        {
            "nome": "Qualidade",
            "responsavel_sugerido": "Qualidade",
            "foco": "checklists, liberacao de etapa e nao conformidades",
        },
        {
            "nome": "Atendimento",
            "responsavel_sugerido": "Relacionamento com cliente",
            "foco": "rascunhos, alinhamentos e aprovacoes com revisao humana",
        },
        {
            "nome": "Gestao",
            "responsavel_sugerido": "Diretoria/Gestao",
            "foco": "decisoes sensiveis, prazo macro e impacto financeiro",
        },
    ]


def _phases() -> list[dict[str, Any]]:
    return [
        _phase(
            "Diagnostico inicial",
            "Planejamento",
            "consolidar escopo, restricoes e riscos iniciais",
            [
                _task("Levantar escopo e restricoes", "Planejamento", ["Checklist", "Foto"], False, False),
                _task("Registrar premissas tecnicas iniciais", "Engenharia", ["Diario de obra"], True, False),
            ],
        ),
        _phase(
            "Planejamento",
            "Planejamento",
            "definir cronograma macro, caminho critico e dependencias",
            [
                _task("Montar cronograma macro", "Planejamento", ["Checklist"], True, False),
                _task("Validar plano de ataque da obra", "Gestao", ["Aprovacao gestao"], True, False),
            ],
        ),
        _phase(
            "Projetos e compatibilizacao",
            "Projetos",
            "compatibilizar disciplinas e liberar detalhe executivo",
            [
                _task("Compatibilizar projetos executivos", "Projetos", ["Projeto", "Checklist"], True, False),
                _task("Resolver pendencias de projeto antes do campo", "Projetos", ["Projeto"], False, False),
            ],
        ),
        _phase(
            "Compras",
            "Compras",
            "garantir especificacao, cotacao e prazo de fornecimento",
            [
                _task("Validar mapa de compras criticas", "Compras", ["Orcamento"], True, False),
                _task("Confirmar fornecedor e prazo de entrega", "Compras", ["Orcamento", "Checklist"], False, False),
            ],
        ),
        _phase(
            "Execucao acompanhada",
            "Engenharia",
            "acompanhar campo com evidencias e controle de retrabalho",
            [
                _task("Registrar execucao de campo", "Engenharia", ["Foto", "Diario de obra"], False, False),
                _task("Tratar divergencia executiva", "Engenharia", ["Foto", "Projeto"], True, False),
            ],
        ),
        _phase(
            "Medicoes",
            "Financeiro",
            "validar medicao, custos e impacto financeiro antes de aprovar",
            [
                _task("Validar medicao da semana", "Financeiro", ["Medicao", "Nota fiscal"], True, False),
                _task("Conferir previsto x realizado", "Financeiro", ["Medicao"], True, False),
            ],
        ),
        _phase(
            "Qualidade",
            "Qualidade",
            "liberar etapas com checklist e evidencias completas",
            [
                _task("Liberar checklist de qualidade", "Qualidade", ["Checklist", "Foto"], False, False),
                _task("Registrar nao conformidade e correcao", "Qualidade", ["Checklist", "Foto"], True, False),
            ],
        ),
        _phase(
            "Entrega",
            "Atendimento",
            "preparar entrega assistida e alinhamento final com cliente",
            [
                _task("Preparar termo de entrega assistida", "Atendimento", ["Checklist"], True, True),
                _task("Gerar rascunho de comunicacao de entrega", "Atendimento", ["Aprovacao cliente"], False, True),
            ],
        ),
        _phase(
            "Pos-obra",
            "Atendimento",
            "registrar aprendizados, garantias e proximos acompanhamentos",
            [
                _task("Consolidar plano de pos-obra", "Atendimento", ["Checklist"], False, True),
                _task("Registrar licoes aprendidas da obra", "Gestao", ["Checklist"], True, False),
            ],
        ),
    ]


def _phase(
    name: str,
    lead_department: str,
    objective: str,
    tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "nome": name,
        "departamento_lider": lead_department,
        "objetivo": objective,
        "tarefas_padrao": tasks,
    }


def _task(
    name: str,
    department: str,
    required_evidence: list[str],
    needs_management_approval: bool,
    needs_client_approval: bool,
) -> dict[str, Any]:
    return {
        "task_name": name,
        "department": department,
        "required_evidence": required_evidence,
        "suggested_owner": department,
        "common_risks": _common_risks_for(department),
        "needs_management_approval": needs_management_approval,
        "needs_client_approval": needs_client_approval,
        "dry_run": True,
        "external_operations": [],
    }


def _common_risks_for(department: str) -> list[str]:
    risks = {
        "Planejamento": ["dependencia nao mapeada", "prazo macro pressionado"],
        "Projetos": ["versao divergente", "conflito de compatibilizacao"],
        "Compras": ["lead time critico", "fornecedor sem confirmacao"],
        "Engenharia": ["evidencia de campo incompleta", "retrabalho"],
        "Financeiro": ["impacto financeiro sem aprovacao", "medicao divergente"],
        "Qualidade": ["checklist incompleto", "pendencia de liberacao"],
        "Atendimento": ["decisao de cliente sem revisao", "comunicacao prematura"],
        "Gestao": ["decisao sensivel sem historico", "impacto financeiro alto"],
    }
    return risks.get(department, ["pendencia operacional"])
