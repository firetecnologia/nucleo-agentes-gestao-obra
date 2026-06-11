from __future__ import annotations

from typing import Any

from .asana_payloads import AsanaTaskReference, PlannedAsanaOperation


def planned_internal_comment(
    reference: AsanaTaskReference,
    comment: str,
    *,
    reason: str,
) -> dict[str, Any]:
    return PlannedAsanaOperation(
        operation="planned_internal_comment",
        payload={
            "task_id": reference.task_id,
            "task_name": reference.task_name,
            "obra": reference.obra,
            "department": reference.department,
            "comment": comment,
            "reason": reason,
            "visibility": "internal_team_only",
        },
    ).to_dict()


def planned_internal_task(
    reference: AsanaTaskReference,
    *,
    name: str,
    notes: str,
    department: str,
    reason: str,
) -> dict[str, Any]:
    return PlannedAsanaOperation(
        operation="planned_internal_task",
        payload={
            "source_task_id": reference.task_id,
            "source_task_name": reference.task_name,
            "obra": reference.obra,
            "department": department,
            "name": name,
            "notes": notes,
            "reason": reason,
            "visibility": "internal_team_only",
        },
    ).to_dict()


def planned_field_update(
    reference: AsanaTaskReference,
    fields: dict[str, Any],
    *,
    reason: str,
) -> dict[str, Any]:
    return PlannedAsanaOperation(
        operation="planned_field_update",
        payload={
            "task_id": reference.task_id,
            "obra": reference.obra,
            "department": reference.department,
            "fields": dict(fields),
            "reason": reason,
        },
    ).to_dict()


def planned_task_link(
    reference: AsanaTaskReference,
    *,
    target_department: str | None = None,
) -> dict[str, Any]:
    return PlannedAsanaOperation(
        operation="planned_task_link",
        payload={
            "task_id": reference.task_id,
            "task_name": reference.task_name,
            "obra": reference.obra,
            "department": reference.department,
            "target_department": target_department or reference.department,
            "relationship": "obra_department_task",
        },
    ).to_dict()


def planned_human_review(
    reference: AsanaTaskReference,
    *,
    review_reason: str,
    reviewer_group: str = "Gestao",
) -> dict[str, Any]:
    return PlannedAsanaOperation(
        operation="planned_human_review",
        payload={
            "task_id": reference.task_id,
            "task_name": reference.task_name,
            "obra": reference.obra,
            "department": reference.department,
            "reviewer_group": reviewer_group,
            "review_reason": review_reason,
            "automatic_approval": False,
        },
    ).to_dict()
