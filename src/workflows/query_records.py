from __future__ import annotations

import argparse
import json

from src.storage import RecordRepository
from src.storage.storage_models import VALID_RECORD_TYPES


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta historico local em dry-run.")
    parser.add_argument("--obra", help="Nome da obra para filtrar.")
    parser.add_argument(
        "--record-type",
        choices=sorted(VALID_RECORD_TYPES),
        help="Tipo de registro para filtrar.",
    )
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
    output = repository.query(obra=args.obra, record_type=args.record_type)
    output["dry_run"] = True
    output["external_operations"] = []

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
