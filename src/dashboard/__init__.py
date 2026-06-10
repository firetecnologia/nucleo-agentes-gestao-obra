"""Camada de dashboard em dry-run para indicadores por obra."""

from .dashboard_builder import build_dashboard, build_dashboard_from_dict
from .decision_history import (
    build_decision_history,
    consolidate_pending_decisions,
    filter_decision_history,
    filter_history_by_decision,
    filter_history_by_department,
    filter_history_by_risk,
)
from .metrics import calculate_metrics
from .work_health import calculate_work_health

__all__ = [
    "build_dashboard",
    "build_dashboard_from_dict",
    "build_decision_history",
    "calculate_metrics",
    "calculate_work_health",
    "consolidate_pending_decisions",
    "filter_decision_history",
    "filter_history_by_decision",
    "filter_history_by_department",
    "filter_history_by_risk",
]
