from __future__ import annotations

from .models import TaskPayload


EVIDENCE_KEYWORDS = {
    "foto": ["foto", "imagem", "jpg", "jpeg", "png", "webp"],
    "checklist": ["checklist", "check-list", "lista"],
    "projeto": ["projeto", "dwg", "pdf", "planta"],
    "orcamento": ["orcamento", "orçamento", "cotacao", "cotação"],
    "nota fiscal": ["nota", "nf", "fiscal"],
    "boleto": ["boleto"],
    "medicao": ["medicao", "medição", "medida"],
    "diario de obra": ["diario", "diário", "obra"],
    "aprovacao cliente": ["aprovacao", "aprovação", "cliente"],
    "aprovacao gestao": ["aprovacao", "aprovação", "gestao", "gestão"],
}


def _normalize(value: str) -> str:
    return value.lower().strip()


def _has_evidence(required: str, task: TaskPayload) -> bool:
    required_norm = _normalize(required)
    keywords = EVIDENCE_KEYWORDS.get(required_norm, [required_norm])

    attachment_text = " ".join(att.name.lower() for att in task.attachments)
    comment_text = " ".join(comment.text.lower() for comment in task.comments)
    description_text = (task.description or "").lower()
    full_text = f"{attachment_text} {comment_text} {description_text}"

    return any(keyword in full_text for keyword in keywords)


def validate_evidence(task: TaskPayload) -> tuple[list[str], list[str]]:
    """Return validated and missing evidence labels."""
    validated: list[str] = []
    missing: list[str] = []

    for required in task.evidencia_obrigatoria:
        if _has_evidence(required, task):
            validated.append(required)
        else:
            missing.append(required)

    return validated, missing
