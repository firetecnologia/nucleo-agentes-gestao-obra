from __future__ import annotations

from typing import Any
import unicodedata

from .audit_trail import build_audit_entry
from .review_models import ReviewItem


REVIEW_DECISIONS = {"blocked", "ask_client", "escalate_management"}
FINANCIAL_REVIEW_LEVELS = {"medio", "media", "medium", "alto", "alta", "high", "critico", "critica", "critical"}
RISK_REVIEW_LEVELS = {"high", "critical", "alto", "alta", "critico", "critica"}


def requires_human_review(decision: dict[str, Any]) -> bool:
    return bool(review_reasons(decision))


def review_reasons(decision: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    decision_name = _normalize(decision.get("decision"))
    financial_impact = _normalize(
        decision.get("impacto_financeiro")
        or decision.get("financial_impact")
        or decision.get("impactoFinanceiro")
    )
    risk_level = _normalize(decision.get("risk_level") or decision.get("risco"))

    if bool(decision.get("requires_human_review", False)):
        reasons.append("Decisao marcada com requires_human_review=true.")
    if decision_name in REVIEW_DECISIONS:
        reasons.append(f"Decisao sensivel exige revisao humana: {decision_name}.")
    if decision_name == "ask_client" or bool(decision.get("precisa_aprovacao_cliente", False)):
        reasons.append("Decisao de cliente sempre exige revisao humana antes de qualquer envio.")
    if financial_impact in FINANCIAL_REVIEW_LEVELS:
        reasons.append(f"Impacto financeiro {financial_impact} exige revisao humana.")
    if risk_level in RISK_REVIEW_LEVELS:
        reasons.append(f"Risco {risk_level} exige revisao humana.")

    return _dedupe(reasons)


def create_review_item_from_decision(
    decision: dict[str, Any],
    *,
    review_id: str,
) -> ReviewItem | None:
    reasons = review_reasons(decision)
    if not reasons:
        return None

    item = ReviewItem(
        review_id=review_id,
        obra=str(decision.get("obra") or ""),
        task_id=str(decision.get("task_id") or ""),
        decision=str(decision.get("decision") or ""),
        risk_level=str(decision.get("risk_level") or "low"),
        reason=" ".join(reasons),
        audit_trail=[
            build_audit_entry(
                action="review_created",
                status="pending",
                notes="Item criado em fila local dry-run para revisao humana.",
            )
        ],
    )
    return item


def _normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").strip().lower())
    return "".join(char for char in text if not unicodedata.combining(char))


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        if value and value not in deduped:
            deduped.append(value)
    return deduped
