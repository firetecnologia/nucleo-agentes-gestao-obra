from __future__ import annotations

from pathlib import Path
from typing import Any

from src.reports import build_report_from_dict

from .html_exporter import escape, render_document, render_list, slugify, write_html_export


FORBIDDEN_CLIENT_TERMS = {
    "critical": "ponto de atencao",
    "critico": "ponto de atencao",
    "bloqueio": "pendencia de validacao",
    "blocked": "pendencia de validacao",
    "conflito interno": "ponto tecnico em avaliacao",
    "desorganizacao": "ajuste operacional",
    "erro interno": "ajuste tecnico",
    "falha interna": "ajuste tecnico",
    "atraso critico": "ponto de atencao de prazo",
}


def export_client_draft_from_dict(
    data: dict[str, Any],
    *,
    output_dir: str | Path = "exports",
    dry_run: bool = True,
) -> dict[str, Any]:
    report = build_report_from_dict(data, "client_draft").to_dict()
    report["dry_run"] = True
    report["external_operations"] = []
    html_content = render_client_draft_html(report)
    filename = f"rascunho-cliente-{slugify(report.get('obra', 'obra'))}.html"
    result = write_html_export(
        html_content,
        output_dir=output_dir,
        filename=filename,
        export_type="client_draft",
        dry_run=dry_run,
    )
    result["report"] = report
    return result


def render_client_draft_html(report: dict[str, Any]) -> str:
    draft = report.get("client_draft") or {}
    body_text = _sanitize_client_text(draft.get("body") or report.get("summary", ""))
    next_steps = [_sanitize_client_text(item) for item in draft.get("next_steps") or []]
    decisions = [_sanitize_client_text(item) for item in draft.get("pending_client_decisions") or []]
    attention_points = [_sanitize_client_text(item) for item in draft.get("communicable_risks") or []]

    body = f"""
    <section>
      <h2>Aviso de revisao humana</h2>
      <div class="panel">Este rascunho nao deve ser enviado automaticamente. Revisao humana obrigatoria antes de qualquer comunicacao externa.</div>
    </section>
    <section>
      <h2>Mensagem proposta</h2>
      <div class="panel">{escape(body_text)}</div>
    </section>
    <section>
      <h2>Proximos passos</h2>
      {render_list(next_steps)}
    </section>
    <section>
      <h2>Decisoes do cliente</h2>
      {render_list(decisions, empty="Sem decisao pendente do cliente neste rascunho.")}
    </section>
    <section>
      <h2>Pontos de atencao comunicaveis</h2>
      {render_list(attention_points)}
    </section>
    """
    return render_document(
        title=f"Rascunho para cliente - {report.get('obra', '')}",
        subtitle="Previa profissional para revisao interna, sem envio automatico.",
        badge="Revisao humana obrigatoria",
        body=body,
        internal=False,
    )


def _sanitize_client_text(value: str) -> str:
    text = str(value or "")
    lowered = text.lower()
    for forbidden, replacement in FORBIDDEN_CLIENT_TERMS.items():
        while forbidden in lowered:
            start = lowered.find(forbidden)
            end = start + len(forbidden)
            text = text[:start] + replacement + text[end:]
            lowered = text.lower()
    return text
