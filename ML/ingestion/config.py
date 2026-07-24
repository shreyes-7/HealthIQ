"""Loads dataset configuration and resolves repository-relative paths."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "ML" / "configs" / "dataset_config.yaml"


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict:
    """Load the dataset configuration file.

    Raises FileNotFoundError with a clear message if the config is missing,
    rather than failing later with an unrelated KeyError.
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Dataset configuration not found at: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def resolve_repo_path(relative_path: str) -> Path:
    """Resolve a path from the config file relative to the repository root."""
    return REPO_ROOT / relative_path
