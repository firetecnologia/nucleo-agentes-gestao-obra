from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import AppConfig
from src.events.event_processor import EventProcessor
from src.integrations.asana_client import AsanaClient


def load_event(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Processa evento simulado do Asana em dry-run.")
    parser.add_argument("--input", required=True, help="Caminho do JSON do evento.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Executa sem alterar sistemas externos. Este é o padrão da Fase 3.",
    )
    args = parser.parse_args()

    config = AppConfig.from_env()
    asana = AsanaClient.from_config(config, dry_run=True)
    processor = EventProcessor(asana_client=asana, dry_run=True)
    result = processor.process(load_event(args.input))

    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
