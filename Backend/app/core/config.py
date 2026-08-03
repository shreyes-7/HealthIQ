"""Application configuration, sourced entirely from environment variables.

CLAUDE.md: "Never hardcode API keys, passwords, database URLs, secrets, tokens.
Always use environment variables." No default here should be treated as a
production-ready value -- the shipped defaults only make local development
work out of the box.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "HealthIQ Backend API"
    api_version: str = "v1"
    environment: str = "development"
    debug: bool = False

    database_url: str = f"sqlite:///{REPO_ROOT / 'Backend' / 'healthiq.db'}"

    ml_saved_models_dir: Path = REPO_ROOT / "ML" / "saved_models"

    log_level: str = "INFO"

    @property
    def api_prefix(self) -> str:
        return f"/api/{self.api_version}"


@lru_cache
def get_settings() -> Settings:
    """Cached so the environment is parsed once per process, not per request."""
    return Settings()
