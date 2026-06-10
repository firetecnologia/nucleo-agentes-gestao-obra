from __future__ import annotations

import unicodedata

from .models import RiskLevel, TaskPayload


RISK_ORDER = {
    "nenhum": 0,
    "baixo": 1,
    "baixa": 1,
    "medio": 2,
    "media": 2,
    "alto": 3,
    "alta": 3,
    "critico": 4,
    "critica": 4,
}

RISK_NAME: dict[int, RiskLevel] = {
    0: "low",
    1: "low",
    2: "medium",
    3: "high",
    4: "critical",
}


def _score(value: str | None) -> int:
    if not value:
        return 0
    text = unicodedata.normalize("NFKD", value.lower().strip())
    normalized = "".join(char for char in text if not unicodedata.combining(char))
    return RISK_ORDER.get(normalized, 0)


def classify_risk(task: TaskPayload, missing_evidence: list[str]) -> RiskLevel:
    score = max(
        _score(task.impacto_prazo),
        _score(task.impacto_financeiro),
        _score(task.impacto_cliente),
        _score(task.prioridade),
    )

    if missing_evidence and score < 2:
        score = 2

    if task.precisa_aprovacao_gestao and score < 3:
        score = 3

    if task.precisa_aprovacao_cliente and score < 2:
        score = 2

    return RISK_NAME[min(score, 4)]
