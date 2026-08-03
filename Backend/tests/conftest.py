"""Shared pytest fixtures for the backend test suite."""

import pandas as pd
import pytest

from ML.ingestion.config import load_config
from ML.ingestion.loader import load_dataset


@pytest.fixture(scope="session")
def raw_patient_record() -> pd.DataFrame:
    """A single, genuinely fresh raw NHAMCS row -- not from any processed
    split -- for exercising the full raw -> pipeline -> model -> SHAP path."""
    config = load_config()
    raw_dataframe, _metadata = load_dataset(config)
    return raw_dataframe.iloc[[123]].reset_index(drop=True)


@pytest.fixture(scope="session", autouse=True)
def _ensure_database_schema_exists():
    """Guarantees the test suite is self-contained: creates every table
    against Settings.database_url if it doesn't already exist, so tests
    don't depend on `alembic upgrade head` having been run manually first.
    Alembic remains the source of truth for real deployments; this is a
    test-bootstrap convenience only, and a no-op if the schema is already
    current."""
    from Backend.app.db.base import Base
    from Backend.app.db.session import engine
    from Backend.app.models import PredictionRecord  # noqa: F401

    Base.metadata.create_all(bind=engine)
