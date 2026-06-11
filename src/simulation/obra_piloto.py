from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO_PATH = PROJECT_ROOT / "samples" / "obra_piloto_scenario.json"
DEFAULT_HISTORY_DIR = PROJECT_ROOT / "local_data" / "simulations" / "obra_piloto"


def default_scenario_path() -> Path:
    return DEFAULT_SCENARIO_PATH


def default_history_dir() -> Path:
    return DEFAULT_HISTORY_DIR
