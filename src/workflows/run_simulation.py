from __future__ import annotations

import argparse
import json

from src.simulation import load_scenario, run_simulation
from src.simulation.obra_piloto import default_scenario_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Executa simulacao ponta a ponta da obra piloto em dry-run.")
    parser.add_argument(
        "--input",
        default=str(default_scenario_path()),
        help="Caminho do JSON de cenario da obra piloto.",
    )
    parser.add_argument(
        "--history-dir",
        default=None,
        help="Diretorio local para salvar historico simulado.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Executa apenas simulacao local, sem servico externo. Este e o padrao.",
    )
    args = parser.parse_args()

    output = run_simulation(
        load_scenario(args.input),
        dry_run=True,
        history_dir=args.history_dir,
    )
    output["dry_run"] = True
    output["external_operations"] = []

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
