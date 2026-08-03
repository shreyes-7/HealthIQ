"""Structured application logging.

CLAUDE.md: log important events (startup, shutdown, prediction requests,
model loading, errors) but never sensitive information. Every log call
site in this backend that touches a prediction logs only the model
version, risk category, and timing -- never the patient's submitted
age/vitals/demographics from `PatientRecordRequest`.
"""

import logging
import sys

from Backend.app.core.config import Settings

LOGGER_NAME = "healthiq.backend"


def configure_logging(settings: Settings) -> None:
    """Idempotent: safe to call multiple times (e.g. once per lifespan in
    tests that construct several TestClients against the same app)."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(settings.log_level.upper())

    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
