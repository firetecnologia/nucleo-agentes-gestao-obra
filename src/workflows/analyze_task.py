from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.domain.models import TaskPayload


def load_payload(path: str) -> TaskPayload:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return TaskPayload.from_dict(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analisa uma tarefa de obra com o Agente Orquestrador.")
    parser.add_argument("--input", required=True, help="Caminho do JSON da tarefa.")
    parser.add_argument("--dry-run", action="store_true", help="Executa sem alterar sistemas externos.")
    args = parser.parse_args()

    task = load_payload(args.input)
    agent = OrchestratorAgent()
    decision = agent.analyze(task)

    output = decision.to_dict()
    output["dry_run"] = bool(args.dry_run)

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
