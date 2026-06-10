from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn


@dataclass(slots=True)
class AsanaClient:
    """Cliente seguro para preparar a integração futura com Asana.

    A primeira versão do MVP roda em dry-run e não altera o Asana.
    """

    token: str | None = None
    dry_run: bool = True
    allow_real_actions: bool = False

    def post_comment(self, task_id: str, comment: str) -> dict[str, str | bool]:
        if self.dry_run:
            return {
                "operation": "post_comment",
                "dry_run": True,
                "task_id": task_id,
                "comment": comment,
            }
        self._raise_real_actions_disabled()

    def create_task(self, name: str, notes: str, project_id: str | None = None) -> dict[str, str | bool | None]:
        if self.dry_run:
            return {
                "operation": "create_task",
                "dry_run": True,
                "name": name,
                "notes": notes,
                "project_id": project_id,
            }
        self._raise_real_actions_disabled()

    def _raise_real_actions_disabled(self) -> NoReturn:
        raise RuntimeError(
            "Chamadas reais ao Asana estão desabilitadas neste MVP. "
            "Use dry_run=True até a Fase 2 validar autenticação, permissões e revisão humana."
        )
