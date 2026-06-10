from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AsanaClient:
    """Cliente placeholder para integração futura com Asana.

    A primeira versão do MVP roda em dry-run e não altera o Asana.
    """

    token: str | None = None
    dry_run: bool = True

    def post_comment(self, task_id: str, comment: str) -> dict[str, str | bool]:
        if self.dry_run:
            return {"dry_run": True, "task_id": task_id, "comment": comment}
        raise NotImplementedError("Integração real com Asana será implementada na Fase 2.")

    def create_task(self, name: str, notes: str, project_id: str | None = None) -> dict[str, str | bool | None]:
        if self.dry_run:
            return {"dry_run": True, "name": name, "notes": notes, "project_id": project_id}
        raise NotImplementedError("Criação real de tarefa no Asana será implementada na Fase 2.")
