from __future__ import annotations

from .models import AgentDecision, NextTask, TaskPayload
from .risk_classifier import classify_risk
from .evidence_validator import validate_evidence


def _is_high(value: str | None) -> bool:
    if not value:
        return False
    return value.lower().strip() in {"alto", "alta", "critico", "crítico", "critica", "crítica"}


def decide(task: TaskPayload) -> AgentDecision:
    validated, missing = validate_evidence(task)
    risk_level = classify_risk(task, missing)

    actions: list[str] = []
    next_tasks: list[NextTask] = []
    decision = "approved"
    requires_human_review = risk_level in {"medium", "high", "critical"}

    if task.precisa_aprovacao_cliente:
        decision = "ask_client"
        actions.append("Atendimento deve solicitar ou confirmar aprovação do cliente antes de avançar.")
        next_tasks.append(
            NextTask(
                name=f"Solicitar aprovação do cliente — {task.task_name}",
                department="Atendimento",
                suggested_owner="Atendimento",
                suggested_due="24h",
                description="Gerar mensagem clara para o cliente e registrar decisão no Asana.",
            )
        )
    elif task.precisa_aprovacao_gestao or _is_high(task.impacto_financeiro):
        decision = "escalate_management"
        actions.append("Gestão deve revisar antes da aprovação final devido a impacto financeiro ou necessidade de decisão interna.")
    elif missing:
        decision = "request_correction"
        actions.append("Responsável deve complementar evidências obrigatórias antes da liberação da etapa.")
    elif _is_high(task.impacto_prazo):
        decision = "escalate_management"
        actions.append("Planejamento e gestão devem avaliar impacto no cronograma macro.")
    elif _is_high(task.impacto_cliente):
        decision = "ask_client"
        actions.append("Atendimento deve preparar comunicação preventiva para o cliente.")
    else:
        decision = "approved"
        requires_human_review = False
        actions.append("Entrega aprovada para seguir ao próximo departamento ou etapa planejada.")

    analysis = _build_analysis(task, validated, missing, risk_level)
    asana_comment = _build_asana_comment(task, decision, risk_level, missing, actions)

    return AgentDecision(
        decision=decision,  # type: ignore[arg-type]
        risk_level=risk_level,
        analysis=analysis,
        asana_comment=asana_comment,
        validated_evidence=validated,
        missing_evidence=missing,
        recommended_actions=actions,
        next_tasks=next_tasks,
        requires_human_review=requires_human_review,
    )


def _build_analysis(
    task: TaskPayload,
    validated: list[str],
    missing: list[str],
    risk_level: str,
) -> str:
    if missing:
        return (
            f"A tarefa '{task.task_name}' possui evidências parciais. "
            f"Foram validadas: {', '.join(validated) or 'nenhuma'}. "
            f"Faltam: {', '.join(missing)}. Nível de risco: {risk_level}."
        )

    return (
        f"A tarefa '{task.task_name}' possui evidências suficientes para análise inicial. "
        f"Nível de risco: {risk_level}."
    )


def _build_asana_comment(
    task: TaskPayload,
    decision: str,
    risk_level: str,
    missing: list[str],
    actions: list[str],
) -> str:
    missing_text = ", ".join(missing) if missing else "nenhuma evidência obrigatória pendente"
    action_text = " ".join(actions)
    return (
        f"Análise do agente — Obra: {task.obra}. "
        f"Tarefa: {task.task_name}. "
        f"Decisão: {decision}. "
        f"Risco: {risk_level}. "
        f"Pendências de evidência: {missing_text}. "
        f"Próxima ação: {action_text}"
    )
