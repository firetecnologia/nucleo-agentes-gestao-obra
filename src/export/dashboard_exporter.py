from __future__ import annotations

from pathlib import Path
from typing import Any

from src.dashboard import build_dashboard_from_dict

from .html_exporter import render_document, render_key_values, render_list, render_table, slugify, write_html_export


def export_dashboard_from_dict(
    data: dict[str, Any],
    *,
    output_dir: str | Path = "exports",
    dry_run: bool = True,
) -> dict[str, Any]:
    dashboard = build_dashboard_from_dict(data).to_dict()
    dashboard["dry_run"] = True
    dashboard["external_operations"] = []
    html_content = render_dashboard_html(dashboard)
    filename = f"dashboard-{slugify(dashboard.get('obra', 'obra'))}.html"
    result = write_html_export(
        html_content,
        output_dir=output_dir,
        filename=filename,
        export_type="dashboard",
        dry_run=dry_run,
    )
    result["dashboard"] = dashboard
    return result


def render_dashboard_html(dashboard: dict[str, Any]) -> str:
    metrics = dashboard.get("metrics") or {}
    body = f"""
    <section>
      <h2>Saude da obra</h2>
      {render_key_values({
        "Status": dashboard.get("health_status", ""),
        "Indice de saude": metrics.get("health_index", 0),
        "Tarefas analisadas": metrics.get("total_tasks_analyzed", 0),
        "Revisoes humanas": metrics.get("human_review_count", 0),
      })}
    </section>
    <section>
      <h2>Gargalos</h2>
      {render_key_values(metrics.get("department_bottlenecks") or {})}
    </section>
    <section>
      <h2>Decisoes pendentes</h2>
      {render_table(
        ["Tarefa", "Departamento", "Decisao", "Risco"],
        [
            [
                item.get("task_name", item.get("task_id", "")),
                item.get("department", ""),
                item.get("decision", ""),
                item.get("risk_level", ""),
            ]
            for item in dashboard.get("pending_decisions") or []
        ],
      )}
    </section>
    <section>
      <h2>Historico de decisoes</h2>
      {render_table(
        ["Tarefa", "Departamento", "Decisao", "Risco", "Origem"],
        [
            [
                item.get("task_name", item.get("task_id", "")),
                item.get("department", ""),
                item.get("decision", ""),
                item.get("risk_level", ""),
                item.get("source", ""),
            ]
            for item in dashboard.get("decision_history") or []
        ],
      )}
    </section>
    <section>
      <h2>Acoes recomendadas de gestao</h2>
      {render_list(dashboard.get("recommended_management_actions") or [])}
    </section>
    """
    return render_document(
        title=f"Dashboard executivo - {dashboard.get('obra', '')}",
        subtitle=f"Cliente: {dashboard.get('cliente', '')}. Documento local para acompanhamento da gestao.",
        badge="Dashboard da obra",
        body=body,
        internal=True,
    )
