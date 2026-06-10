from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .routes_analysis import analyze_task_endpoint
from .routes_dashboard import generate_dashboard_endpoint
from .routes_events import process_event_endpoint
from .routes_reports import generate_report_endpoint
from .schemas import ApiResponse, RouteDefinition, response


Handler = Callable[[dict[str, Any]], dict[str, Any]]


class LocalApiApp:
    """Camada API-like em dry-run, sem dependencia externa nesta fase."""

    def __init__(self) -> None:
        self._routes: dict[tuple[str, str], Handler] = {}
        self.route_definitions: list[RouteDefinition] = []

    def add_route(
        self,
        method: str,
        path: str,
        handler: Handler,
        *,
        description: str,
    ) -> None:
        method_key = method.upper()
        path_key = _normalize_path(path)
        self._routes[(method_key, path_key)] = handler
        self.route_definitions.append(
            RouteDefinition(
                method=method_key,  # type: ignore[arg-type]
                path=path_key,
                handler_name=handler.__name__,
                description=description,
            )
        )

    def get(self, path: str) -> ApiResponse:
        return self.handle("GET", path)

    def post(self, path: str, payload: dict[str, Any]) -> ApiResponse:
        return self.handle("POST", path, payload)

    def handle(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> ApiResponse:
        method_key = method.upper()
        path_key = _normalize_path(path)

        if method_key == "GET" and path_key == "/health":
            return response(
                {
                    "status": "ok",
                    "service": "nucleo-agentes-gestao-obra",
                    "routes": [route.to_dict() for route in self.route_definitions],
                }
            )

        handler = self._routes.get((method_key, path_key))
        if handler is None:
            return response(
                {
                    "status": "not_found",
                    "error": f"Rota nao encontrada: {method_key} {path_key}",
                },
                status_code=404,
            )

        try:
            return response(handler(dict(payload or {})))
        except Exception as exc:  # pragma: no cover - caminho defensivo da API local
            return response(
                {
                    "status": "error",
                    "error": str(exc),
                },
                status_code=400,
            )


def create_app() -> LocalApiApp:
    local_app = LocalApiApp()
    local_app.add_route(
        "POST",
        "/analyze-task",
        analyze_task_endpoint,
        description="Analisa tarefa em dry-run.",
    )
    local_app.add_route(
        "POST",
        "/process-event",
        process_event_endpoint,
        description="Processa evento simulado em dry-run.",
    )
    local_app.add_route(
        "POST",
        "/generate-report",
        generate_report_endpoint,
        description="Gera relatorio em dry-run.",
    )
    local_app.add_route(
        "POST",
        "/generate-dashboard",
        generate_dashboard_endpoint,
        description="Gera dashboard em dry-run.",
    )
    return local_app


def _normalize_path(path: str) -> str:
    normalized = "/" + path.strip("/")
    return normalized if normalized != "/" else "/"


app = create_app()
