from __future__ import annotations

import argparse
import json

from src.review import ReviewQueue
from src.review.review_models import ReviewStatus


def main() -> None:
    parser = argparse.ArgumentParser(description="Atualiza status local de uma revisao humana em dry-run.")
    parser.add_argument("--review-id", required=True, help="ID da revisao, por exemplo REV-001.")
    parser.add_argument(
        "--status",
        required=True,
        choices=["pending", "approved", "rejected", "changes_requested"],
        help="Novo status local da revisao.",
    )
    parser.add_argument("--reviewer", required=True, help="Nome ou grupo revisor.")
    parser.add_argument("--notes", default="", help="Observacao opcional para auditoria.")
    parser.add_argument("--base-dir", default="local_data/reviews", help="Diretorio local da fila de revisao.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Atualiza somente JSON local, sem acao externa. Este e o padrao.",
    )
    args = parser.parse_args()

    try:
        output = ReviewQueue(args.base_dir).update_status(
            args.review_id,
            args.status,  # type: ignore[arg-type]
            reviewer=args.reviewer,
            notes=args.notes,
        )
    except (FileNotFoundError, ValueError) as exc:
        output = {
            "updated": False,
            "dry_run": True,
            "external_operations": [],
            "error": str(exc),
        }

    output["dry_run"] = True
    output["external_operations"] = []
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
