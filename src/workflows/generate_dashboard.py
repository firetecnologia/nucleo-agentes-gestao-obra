from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.dashboard import build_dashboard_from_dict


def load_dashboard_input(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dashboard da obra em dry-run.")
    parser.add_argument("--input", required=True, help="Caminho do JSON de entrada do dashboard.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Gera apenas JSON local, sem canal externo. Este e o padrao.",
    )
    args = parser.parse_args()

    dashboard = build_dashboard_from_dict(load_dashboard_input(args.input))
    output = dashboard.to_dict()
    output["dry_run"] = True
    output["external_operations"] = []

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
