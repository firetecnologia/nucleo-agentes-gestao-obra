from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.storage import RecordRepository


def load_record(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Salva registro local do sistema em dry-run.")
    parser.add_argument("--input", required=True, help="Caminho do JSON do registro.")
    parser.add_argument(
        "--base-dir",
        default="local_data",
        help="Diretorio local de armazenamento. Padrao: local_data.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Mantem operacoes externas desativadas. Este e o padrao.",
    )
    args = parser.parse_args()

    repository = RecordRepository(base_dir=args.base_dir)
    output = repository.save(load_record(args.input))
    output["dry_run"] = True
    output["external_operations"] = []

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
