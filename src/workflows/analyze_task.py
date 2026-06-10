from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.config import AppConfig
from src.domain.models import TaskPayload
from src.integrations.asana_client import AsanaClient


def load_payload(path: str) -> TaskPayload:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TaskPayload.from_dict(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisa uma tarefa de obra com o Agente Orquestrador.")
    parser.add_argument("--input", required=True, help="Caminho do JSON da tarefa.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Executa sem alterar sistemas externos. Este é o padrão do MVP.",
    )
    args = parser.parse_args()

    task = load_payload(args.input)
    agent = OrchestratorAgent()
    decision = agent.analyze(task)
    config = AppConfig.from_env()
    asana = AsanaClient.from_config(config, dry_run=True)

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

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
