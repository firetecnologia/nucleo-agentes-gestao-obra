from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.reports import build_report_from_dict
from src.reports.report_models import ReportType


def load_report_input(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera relatorio da obra em dry-run.")
    parser.add_argument("--input", required=True, help="Caminho do JSON de entrada do relatorio.")
    parser.add_argument(
        "--type",
        required=True,
        choices=["internal_daily", "weekly_management", "client_draft"],
        help="Tipo de relatorio a gerar.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Gera apenas JSON local, sem envio externo. Este e o padrao.",
    )
    args = parser.parse_args()

    report = build_report_from_dict(load_report_input(args.input), args.type)  # type: ignore[arg-type]
    output = report.to_dict()
    output["dry_run"] = True
    output["external_operations"] = []

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
