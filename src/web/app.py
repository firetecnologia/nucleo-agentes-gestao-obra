from __future__ import annotations

import json
from dataclasses import dataclass, field
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from src.dashboard import build_dashboard_from_dict
from src.reports import build_report_from_dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"


@dataclass(slots=True)
class WebResponse:
    status_code: int
    body: str
    content_type: str = "text/html; charset=utf-8"
    dry_run: bool = True
    external_operations: list[dict[str, Any]] = field(default_factory=list)


class LocalWebApp:
    """Interface web local para demonstracao interna em dry-run."""

    def __init__(self, project_root: Path = PROJECT_ROOT) -> None:
        self.project_root = project_root

    def get(self, path: str) -> WebResponse:
        route = _normalize_path(path)
        if route == "/":
            return self._home()
        if route == "/dashboard":
            return self._dashboard()
        if route == "/historico-decisoes":
            return self._decision_history()
        if route == "/relatorio-semanal":
            return self._weekly_report()
        if route == "/rascunho-cliente":
            return self._client_draft()
        if route == "/static/styles.css":
            return WebResponse(
                status_code=200,
                body=(STATIC_DIR / "styles.css").read_text(encoding="utf-8"),
                content_type="text/css; charset=utf-8",
            )
        if route == "/static/nucleo-mark.svg":
            return WebResponse(
                status_code=200,
                body=(STATIC_DIR / "nucleo-mark.svg").read_text(encoding="utf-8"),
                content_type="image/svg+xml; charset=utf-8",
            )
        return WebResponse(
            status_code=404,
            body=_render_page(
                "home.html",
                {
                    "title": "Pagina nao encontrada",
                    "obra": "Obra nao encontrada",
                    "cliente": "",
                    "health_status": "attention",
                    "summary": "Rota local nao encontrada.",
                    "metrics": "",
                    "content": "<p>Rota local nao encontrada.</p>",
                },
            ),
        )

    def _home(self) -> WebResponse:
        dashboard = self._dashboard_data()
        return WebResponse(
            status_code=200,
            body=_render_page(
                "home.html",
                {
                    "title": "Obra",
                    "obra": dashboard["obra"],
                    "cliente": dashboard["cliente"],
                    "health_status": dashboard["health_status"],
                    "summary": _home_summary(dashboard),
                    "metrics": _metric_strip(dashboard["metrics"]),
                    "content": _home_links(),
                },
            ),
        )

    def _dashboard(self) -> WebResponse:
        dashboard = self._dashboard_data()
        return WebResponse(
            status_code=200,
            body=_render_page(
                "dashboard.html",
                {
                    "title": "Dashboard executivo",
                    "obra": dashboard["obra"],
                    "cliente": dashboard["cliente"],
                    "health_status": dashboard["health_status"],
                    "metrics": _metric_cards(dashboard["metrics"]),
                    "active_risks": _list_items(
                        _risk_label(risk) for risk in dashboard["active_risks"]
                    ),
                    "actions": _list_items(dashboard["recommended_management_actions"]),
                    "department_summary": _department_table(dashboard["department_summary"]),
                },
            ),
        )

    def _decision_history(self) -> WebResponse:
        dashboard = self._dashboard_data()
        return WebResponse(
            status_code=200,
            body=_render_page(
                "decision_history.html",
                {
                    "title": "Historico de decisoes",
                    "obra": dashboard["obra"],
                    "cliente": dashboard["cliente"],
                    "health_status": dashboard["health_status"],
                    "decision_history": _decision_history_table(dashboard["decision_history"]),
                },
            ),
        )

    def _weekly_report(self) -> WebResponse:
        report = self._weekly_report_data()
        return WebResponse(
            status_code=200,
            body=_render_page(
                "weekly_report.html",
                {
                    "title": "Relatorio semanal",
                    "obra": report["obra"],
                    "health_status": report["health_status"],
                    "summary": report["summary"],
                    "highlights": _list_items(report["highlights"]),
                    "risks": _list_items(report["risks"]),
                    "pending_decisions": _list_items(report["pending_decisions"]),
                    "actions": _list_items(report["recommended_actions"]),
                },
            ),
        )

    def _client_draft(self) -> WebResponse:
        report = self._client_draft_data()
        client_draft = report["client_draft"] or {}
        return WebResponse(
            status_code=200,
            body=_render_page(
                "client_draft.html",
                {
                    "title": "Rascunho para cliente",
                    "obra": report["obra"],
                    "health_status": report["health_status"],
                    "review_notice": "Revisao humana obrigatoria antes de qualquer envio.",
                    "body": _paragraph(client_draft.get("body", "")),
                    "next_steps": _list_items(client_draft.get("next_steps") or []),
                    "pending_client_decisions": _list_items(
                        client_draft.get("pending_client_decisions") or []
                    ),
                    "external_delivery": client_draft.get("external_delivery", "draft_only_no_external_send"),
                },
            ),
        )

    def _dashboard_data(self) -> dict[str, Any]:
        data = _load_json(self.project_root / "samples" / "dashboard_input_obra.json")
        output = build_dashboard_from_dict(data).to_dict()
        output["dry_run"] = True
        output["external_operations"] = []
        return output

    def _weekly_report_data(self) -> dict[str, Any]:
        data = _load_json(self.project_root / "samples" / "report_input_weekly.json")
        output = build_report_from_dict(data, "weekly_management").to_dict()
        output["dry_run"] = True
        output["external_operations"] = []
        return output

    def _client_draft_data(self) -> dict[str, Any]:
        data = _load_json(self.project_root / "samples" / "report_input_weekly.json")
        output = build_report_from_dict(data, "client_draft").to_dict()
        output["dry_run"] = True
        output["external_operations"] = []
        return output


def create_web_app(project_root: Path = PROJECT_ROOT) -> LocalWebApp:
    return LocalWebApp(project_root=project_root)


def run_local_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    app = create_web_app()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - assinatura exigida por BaseHTTPRequestHandler
            response = app.get(self.path)
            encoded = response.body.encode("utf-8")
            self.send_response(response.status_code)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    ThreadingHTTPServer((host, port), Handler).serve_forever()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _render_page(template_name: str, context: dict[str, Any]) -> str:
    template = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    values = {key: str(value) for key, value in context.items()}
    for key, value in values.items():
        template = template.replace("{{ " + key + " }}", value)
    return template


def _home_summary(dashboard: dict[str, Any]) -> str:
    metrics = dashboard["metrics"]
    return (
        f"{metrics['total_tasks_analyzed']} tarefas analisadas, "
        f"{metrics['approved_count']} aprovadas, "
        f"{metrics['human_review_count']} em revisao humana."
    )


def _home_links() -> str:
    links = [
        ("/dashboard", "Dashboard executivo"),
        ("/historico-decisoes", "Historico de decisoes"),
        ("/relatorio-semanal", "Relatorio semanal"),
        ("/rascunho-cliente", "Rascunho para cliente"),
    ]
    return "<nav class=\"quick-links\">" + "".join(
        f"<a href=\"{href}\">{escape(label)}</a>" for href, label in links
    ) + "</nav>"


def _metric_strip(metrics: dict[str, Any]) -> str:
    return _metric_cards(
        {
            "health_index": metrics["health_index"],
            "approval_rate": metrics["approval_rate"],
            "rework_pending_rate": metrics["rework_pending_rate"],
        }
    )


def _metric_cards(metrics: dict[str, Any]) -> str:
    cards = []
    labels = {
        "total_tasks_analyzed": "Tarefas",
        "approved_count": "Aprovadas",
        "correction_count": "Correcoes",
        "blocked_count": "Bloqueios",
        "human_review_count": "Revisao humana",
        "high_risk_count": "Risco alto",
        "critical_risk_count": "Risco critico",
        "client_decision_count": "Decisoes cliente",
        "financial_impact_count": "Impacto financeiro",
        "approval_rate": "Taxa aprovacao",
        "rework_pending_rate": "Retrabalho/pendencia",
        "health_index": "Indice saude",
    }
    for key, label in labels.items():
        if key in metrics:
            value = metrics[key]
            if key.endswith("_rate"):
                value = f"{float(value) * 100:.0f}%"
            cards.append(
                f"<article class=\"metric\"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></article>"
            )
    return "<section class=\"metrics\">" + "".join(cards) + "</section>"


def _department_table(summary: dict[str, dict[str, int]]) -> str:
    rows = []
    for department, values in summary.items():
        rows.append(
            "<tr>"
            f"<td>{escape(department)}</td>"
            f"<td>{values.get('total', 0)}</td>"
            f"<td>{values.get('approved', 0)}</td>"
            f"<td>{values.get('human_review', 0)}</td>"
            f"<td>{values.get('bottlenecks', 0)}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Departamento</th><th>Total</th><th>Aprovadas</th>"
        "<th>Revisao</th><th>Gargalos</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _decision_history_table(history: list[dict[str, Any]]) -> str:
    rows = []
    for entry in history:
        rows.append(
            "<tr>"
            f"<td>{escape(entry.get('created_at') or '')}</td>"
            f"<td>{escape(entry.get('task_name') or entry.get('task_id') or '')}</td>"
            f"<td>{escape(entry.get('department') or '')}</td>"
            f"<td>{escape(entry.get('decision') or '')}</td>"
            f"<td>{escape(entry.get('risk_level') or '')}</td>"
            f"<td>{'Sim' if entry.get('requires_human_review') else 'Nao'}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Data</th><th>Tarefa</th><th>Departamento</th>"
        "<th>Decisao</th><th>Risco</th><th>Revisao</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )


def _risk_label(risk: dict[str, Any]) -> str:
    return (
        f"{risk.get('task_name') or risk.get('task_id')} - "
        f"{risk.get('department')} - risco {risk.get('risk_level')}"
    )


def _list_items(values: Any) -> str:
    items = list(values or [])
    if not items:
        return "<p class=\"empty\">Sem itens neste momento.</p>"
    return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in items) + "</ul>"


def _paragraph(value: str) -> str:
    return f"<p>{escape(value)}</p>"


def _normalize_path(path: str) -> str:
    route = path.split("?", 1)[0]
    normalized = "/" + route.strip("/")
    return normalized if normalized != "/" else "/"


app = create_web_app()


if __name__ == "__main__":
    run_local_server()
