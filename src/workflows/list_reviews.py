from __future__ import annotations

import argparse
import json

from src.review import ReviewQueue


def main() -> None:
    parser = argparse.ArgumentParser(description="Lista revisoes humanas pendentes em dry-run.")
    parser.add_argument("--base-dir", default="local_data/reviews", help="Diretorio local da fila de revisao.")
    parser.add_argument(
        "--status",
        choices=["pending", "approved", "rejected", "changes_requested"],
        default=None,
        help="Filtra por status local.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Consulta somente fila local, sem acao externa. Este e o padrao.",
    )
    args = parser.parse_args()

    output = ReviewQueue(args.base_dir).list_reviews(status=args.status)
    output["dry_run"] = True
    output["external_operations"] = []
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
