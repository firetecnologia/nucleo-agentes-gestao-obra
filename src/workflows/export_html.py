from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from src.export import (
    export_client_draft_from_dict,
    export_dashboard_from_dict,
    export_simulation_summary,
    export_weekly_report_from_dict,
)
from src.simulation import SimulationRunner


def load_input(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta relatorios e dashboard em HTML local dry-run.")
    parser.add_argument("--input", required=True, help="Caminho do JSON de entrada.")
    parser.add_argument(
        "--type",
        required=True,
        choices=["dashboard", "weekly_report", "client_draft", "simulation_summary"],
        help="Tipo de HTML a exportar.",
    )
    parser.add_argument(
        "--output-dir",
        default="exports",
        help="Pasta local de saida dos arquivos HTML.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Exporta apenas arquivo local, sem envio externo. Este e o padrao.",
    )
    args = parser.parse_args()

    data = load_input(args.input)
    if args.type == "dashboard":
        result = export_dashboard_from_dict(data, output_dir=args.output_dir, dry_run=True)
    elif args.type == "weekly_report":
        result = export_weekly_report_from_dict(data, output_dir=args.output_dir, dry_run=True)
    elif args.type == "client_draft":
        result = export_client_draft_from_dict(data, output_dir=args.output_dir, dry_run=True)
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            simulation_output = SimulationRunner(history_dir=temp_dir).run(data)
        result = export_simulation_summary(simulation_output, output_dir=args.output_dir, dry_run=True)

    result["dry_run"] = True
    result["external_operations"] = []
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
