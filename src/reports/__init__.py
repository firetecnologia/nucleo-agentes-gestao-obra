"""Camada de relatorios em dry-run para a Nucleo 377."""

from .report_builder import build_report, build_report_from_dict, classify_health_status

__all__ = ["build_report", "build_report_from_dict", "classify_health_status"]
