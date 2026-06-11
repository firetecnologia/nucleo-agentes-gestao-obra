"""Interface web local em dry-run para demonstracao interna."""

from .app import LocalWebApp, app, create_web_app

__all__ = ["LocalWebApp", "app", "create_web_app"]
