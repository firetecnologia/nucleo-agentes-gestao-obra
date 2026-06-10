from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, NoReturn

from src.config import AppConfig


@dataclass(slots=True)
class AsanaClient:
    """Cliente seguro para preparar a integração futura com Asana.

    A primeira versão do MVP roda em dry-run e não altera o Asana.
    """

    token: str | None = None
    workspace_gid: str | None = None
    project_gid: str | None = None
    dry_run: bool = True
    enable_real_actions: bool = False
    confirm_real_action: bool = False

    @classmethod
    def from_config(
        cls,
        config: AppConfig,
        *,
        dry_run: bool | None = None,
        confirm_real_action: bool = False,
    ) -> "AsanaClient":
        return cls(
            token=config.asana_access_token,
            workspace_gid=config.asana_workspace_gid,
            project_gid=config.asana_project_gid,
            dry_run=config.dry_run if dry_run is None else dry_run,
            enable_real_actions=config.asana_enable_real_actions,
            confirm_real_action=confirm_real_action,
        )

    def fetch_task(self, task_id: str) -> dict[str, Any]:
        if self.dry_run:
            return self._planned_operation("fetch_task", task_id=task_id)
        self._raise_stub_after_guard("fetch_task")

    def post_comment(self, task_id: str, comment: str) -> dict[str, Any]:
        if self.dry_run:
            return self._planned_operation("post_comment", task_id=task_id, comment=comment)
        self._raise_stub_after_guard("post_comment")

    def create_task(
        self,
        name: str,
        notes: str,
        project_id: str | None = None,
        assignee_gid: str | None = None,
        due_on: str | None = None,
    ) -> dict[str, Any]:
        if self.dry_run:
            return self._planned_operation(
                "create_task",
                name=name,
                notes=notes,
                project_id=project_id or self.project_gid,
                assignee_gid=assignee_gid,
                due_on=due_on,
            )
        self._raise_stub_after_guard("create_task")

    def update_fields(self, task_id: str, fields: Mapping[str, Any]) -> dict[str, Any]:
        if self.dry_run:
            return self._planned_operation(
                "update_fields",
                task_id=task_id,
                fields=dict(fields),
            )
        self._raise_stub_after_guard("update_fields")

    def _planned_operation(self, operation: str, **payload: Any) -> dict[str, Any]:
        return {
            "operation": operation,
            "dry_run": True,
            **payload,
        }

    def _ensure_real_actions_allowed(self) -> None:
        if self.dry_run:
            return
        if not self.enable_real_actions:
            raise RuntimeError(
                "Chamada real ao Asana bloqueada: ASANA_ENABLE_REAL_ACTIONS precisa ser true."
            )
        if not self.token:
            raise RuntimeError(
                "Chamada real ao Asana bloqueada: ASANA_ACCESS_TOKEN não foi configurado."
            )
        if not self.confirm_real_action:
            raise RuntimeError(
                "Chamada real ao Asana bloqueada: falta confirmação explícita no código."
            )

    def _raise_stub_after_guard(self, operation: str) -> NoReturn:
        self._ensure_real_actions_allowed()
        raise NotImplementedError(
            f"Operação real '{operation}' ainda é um stub seguro da Fase 2. "
            "Nenhuma chamada ao Asana foi executada."
        )
