from __future__ import annotations

import unicodedata

from .models import TaskPayload


EVIDENCE_KEYWORDS = {
    "foto": ["foto", "imagem", "jpg", "jpeg", "png", "webp"],
    "checklist": ["checklist", "check-list", "lista"],
    "projeto": ["projeto", "dwg", "pdf", "planta"],
    "orcamento": ["orcamento", "cotacao"],
    "nota fiscal": ["nota", "nf", "fiscal"],
    "boleto": ["boleto"],
    "medicao": ["medicao", "medida"],
    "diario de obra": ["diario"],
    "aprovacao cliente": ["aprovacao", "cliente"],
    "aprovacao gestao": ["aprovacao", "gestao"],
}


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower().strip())
    return "".join(char for char in text if not unicodedata.combining(char))


def _has_evidence(required: str, task: TaskPayload) -> bool:
    required_norm = _normalize(required)
    keywords = EVIDENCE_KEYWORDS.get(required_norm, [required_norm])

    attachment_text = " ".join(_normalize(att.name) for att in task.attachments)
    comment_text = " ".join(_normalize(comment.text) for comment in task.comments)
    description_text = _normalize(task.description or "")
    full_text = f"{attachment_text} {comment_text} {description_text}"

    return any(_normalize(keyword) in full_text for keyword in keywords)


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
