from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT_DIR = "exports"


def escape(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower().strip())
    normalized = "".join(char for char in text if not unicodedata.combining(char))
    safe = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return safe or "export"


def render_document(
    *,
    title: str,
    subtitle: str,
    badge: str,
    body: str,
    internal: bool,
) -> str:
    document_type = "DOCUMENTO INTERNO" if internal else "RASCUNHO PARA REVISAO HUMANA"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --ink: #17202a;
      --muted: #68717d;
      --line: #d8dee6;
      --panel: #f7f9fb;
      --brand: #214f4b;
      --accent: #b58a35;
      --soft: #eef4f2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: #ffffff;
      line-height: 1.5;
    }}
    .page {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 40px 32px 56px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 24px;
      margin-bottom: 28px;
    }}
    .eyebrow {{
      color: var(--brand);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 8px 0;
      font-size: 30px;
      line-height: 1.18;
    }}
    h2 {{
      margin: 26px 0 10px;
      font-size: 18px;
      color: var(--brand);
    }}
    h3 {{
      margin: 18px 0 8px;
      font-size: 15px;
    }}
    .subtitle {{
      color: var(--muted);
      margin: 0;
      max-width: 780px;
    }}
    .badge {{
      display: inline-block;
      margin-top: 16px;
      padding: 6px 10px;
      border: 1px solid var(--line);
      background: var(--soft);
      color: var(--brand);
      font-size: 12px;
      font-weight: 700;
    }}
    .notice {{
      margin-top: 12px;
      padding: 12px 14px;
      background: var(--panel);
      border-left: 4px solid var(--accent);
      color: var(--muted);
      font-size: 13px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
    }}
    .metric, .panel {{
      border: 1px solid var(--line);
      background: #fff;
      padding: 14px;
    }}
    .metric strong {{
      display: block;
      font-size: 24px;
      color: var(--brand);
    }}
    ul {{
      padding-left: 20px;
      margin-top: 8px;
    }}
    li {{ margin: 5px 0; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      vertical-align: top;
    }}
    th {{
      color: var(--brand);
      background: var(--panel);
    }}
    footer {{
      margin-top: 36px;
      color: var(--muted);
      font-size: 12px;
      border-top: 1px solid var(--line);
      padding-top: 14px;
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div class="eyebrow">Nucleo 377</div>
      <h1>{escape(title)}</h1>
      <p class="subtitle">{escape(subtitle)}</p>
      <span class="badge">{escape(badge)}</span>
      <div class="notice">{document_type}. Gerado localmente em dry-run; sem envio externo, sem Asana real e sem canais reais.</div>
    </header>
    {body}
    <footer>dry_run=true | external_operations=[] | exportacao local HTML</footer>
  </main>
</body>
</html>
"""


def render_list(items: list[Any], *, empty: str = "Sem itens para exibir.") -> str:
    if not items:
        return f"<p>{escape(empty)}</p>"
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def render_key_values(values: dict[str, Any]) -> str:
    if not values:
        return "<p>Sem indicadores para exibir.</p>"
    items = "".join(
        f"<div class=\"metric\"><span>{escape(label)}</span><strong>{escape(value)}</strong></div>"
        for label, value in values.items()
    )
    return f"<div class=\"grid\">{items}</div>"


def render_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "<p>Sem registros para exibir.</p>"
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table>"


def write_html_export(
    html_content: str,
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    filename: str,
    export_type: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename
    file_path.write_text(html_content, encoding="utf-8")

    return {
        "export_type": export_type,
        "path": str(file_path),
        "filename": filename,
        "dry_run": True,
        "external_operations": [],
        "bytes": file_path.stat().st_size,
        "message": "HTML exportado localmente em modo dry-run.",
    }


def export_simulation_summary(
    simulation_output: dict[str, Any],
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    dry_run: bool = True,
) -> dict[str, Any]:
    body = f"""
    <section>
      <h2>Resumo da simulacao</h2>
      {render_key_values({
        "Obra": simulation_output.get("obra", ""),
        "Cliente": simulation_output.get("cliente", ""),
        "Analises": len(simulation_output.get("analyses") or []),
        "Eventos processados": len(simulation_output.get("events_processed") or []),
        "Operacoes planejadas": len(simulation_output.get("planned_operations") or []),
      })}
    </section>
    <section>
      <h2>Decisoes analisadas</h2>
      {render_table(
        ["Tarefa", "Decisao", "Risco", "Revisao humana"],
        [
            [
                item.get("task_name", item.get("task_id", "")),
                item.get("decision", ""),
                item.get("risk_level", ""),
                "sim" if item.get("requires_human_review") else "nao",
            ]
            for item in simulation_output.get("analyses") or []
        ],
      )}
    </section>
    <section>
      <h2>Saude da obra na simulacao</h2>
      <div class="panel">{escape((simulation_output.get("dashboard") or {}).get("health_status", ""))}</div>
    </section>
    """
    html_content = render_document(
        title=f"Resumo da simulacao - {simulation_output.get('obra', 'Obra piloto')}",
        subtitle="Consolidado local da simulacao ponta a ponta da obra piloto.",
        badge="Simulacao dry-run",
        body=body,
        internal=True,
    )
    filename = f"simulacao-{slugify(str(simulation_output.get('obra', 'obra-piloto')))}.html"
    return write_html_export(
        html_content,
        output_dir=output_dir,
        filename=filename,
        export_type="simulation_summary",
        dry_run=dry_run,
    )
