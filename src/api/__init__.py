"""API interna local em dry-run, sem dependencias externas nesta fase."""

from .app import LocalApiApp, app, create_app

__all__ = ["LocalApiApp", "app", "create_app"]
