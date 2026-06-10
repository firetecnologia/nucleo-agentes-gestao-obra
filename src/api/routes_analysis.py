from __future__ import annotations

from typing import Any

from src.agents.orchestrator import OrchestratorAgent
from src.config import AppConfig
from src.domain.models import TaskPayload
from src.integrations.asana_client import AsanaClient


def analyze_task_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
    task = TaskPayload.from_dict(payload)
    decision = OrchestratorAgent().analyze(task)
    asana = AsanaClient.from_config(AppConfig.from_env({}), dry_run=True)

    output = decision.to_dict()
    output["dry_run"] = True
    output["planned_asana_operations"] = [
        asana.post_comment(task.task_id, decision.asana_comment),
        *[
            asana.create_task(
                name=next_task.name,
                notes=next_task.description,
            )
            for next_task in decision.next_tasks
        ],
    ]
    output["external_operations"] = []
    return output
