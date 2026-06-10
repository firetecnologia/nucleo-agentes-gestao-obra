from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


TRUE_VALUES = {"1", "true", "t", "yes", "y", "sim", "s", "on"}
FALSE_VALUES = {"0", "false", "f", "no", "n", "nao", "não", "off", ""}


def parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    return default


def _optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@dataclass(frozen=True, slots=True)
class AppConfig:
    dry_run: bool = True
    asana_access_token: str | None = None
    asana_workspace_gid: str | None = None
    asana_project_gid: str | None = None
    asana_enable_real_actions: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AppConfig":
        source = os.environ if env is None else env
        return cls(
            dry_run=parse_bool(source.get("DRY_RUN"), default=True),
            asana_access_token=_optional(source.get("ASANA_ACCESS_TOKEN")),
            asana_workspace_gid=_optional(source.get("ASANA_WORKSPACE_GID")),
            asana_project_gid=_optional(source.get("ASANA_PROJECT_GID")),
            asana_enable_real_actions=parse_bool(
                source.get("ASANA_ENABLE_REAL_ACTIONS"),
                default=False,
            ),
        )
