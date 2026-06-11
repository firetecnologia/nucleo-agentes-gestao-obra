from __future__ import annotations

from pathlib import Path
from typing import Any

from src.reports import build_report_from_dict

from .html_exporter import escape, render_document, render_key_values, render_list, slugify, write_html_export


def export_weekly_report_from_dict(
    data: dict[str, Any],
    *,
    output_dir: str | Path = "exports",
    dry_run: bool = True,
) -> dict[str, Any]:
    report = build_report_from_dict(data, "weekly_management").to_dict()
    report["dry_run"] = True
    report["external_operations"] = []
    html_content = render_weekly_report_html(report)
    filename = f"relatorio-semanal-{slugify(report.get('obra', 'obra'))}.html"
    result = write_html_export(
        html_content,
        output_dir=output_dir,
        filename=filename,
        export_type="weekly_report",
        dry_run=dry_run,
    )
    result["report"] = report
    return result


def render_weekly_report_html(report: dict[str, Any]) -> str:
    period = report.get("period") or {}
    body = f"""
    <section>
      <h2>Saude da obra</h2>
      {render_key_values({
        "Status": report.get("health_status", ""),
        "Inicio": period.get("inicio", ""),
        "Fim": period.get("fim", ""),
        "Revisao humana": "sim" if report.get("requires_human_review") else "nao",
      })}
    </section>
    <section>
      <h2>Resumo executivo</h2>
      <div class="panel">{escape(report.get("summary", ""))}</div>
    </section>
    <section>
      <h2>Avancos e destaques</h2>
      {render_list(report.get("highlights") or report.get("approved_tasks") or [])}
    </section>
    <section>
      <h2>Gargalos e riscos</h2>
      {render_list((report.get("risks") or []) + (report.get("deadline_impacts") or []) + (report.get("financial_impacts") or []))}
    </section>
    <section>
      <h2>Decisoes pendentes</h2>
      {render_list(report.get("pending_decisions") or report.get("management_decisions") or [])}
    </section>
    <section>
      <h2>Acoes recomendadas</h2>
      {render_list(report.get("recommended_actions") or report.get("next_actions") or [])}
    </section>
    """
    return render_document(
        title=f"Relatorio semanal executivo - {report.get('obra', '')}",
        subtitle="Visao executiva local para gestao da obra, sem envio externo.",
        badge="Relatorio semanal",
        body=body,
        internal=True,
    )
