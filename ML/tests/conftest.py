"""Shared pytest fixtures for the ML test suite."""

import pandas as pd
import pytest

from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config
from ML.ingestion.loader import load_dataset


@pytest.fixture(scope="session")
def raw_dataframe() -> pd.DataFrame:
    """The full raw dataset, loaded once per test session."""
    config = load_config(DEFAULT_CONFIG_PATH)
    dataframe, _metadata = load_dataset(config)
    return dataframe


@pytest.fixture(scope="session")
def small_raw_sample(raw_dataframe) -> pd.DataFrame:
    """A small, fast-to-process slice of real raw data for pipeline-level
    integration tests. 401 rows (odd count) deliberately, so any median
    computed on it always lands on an actual data point rather than the
    midpoint between two -- test_imputation.py separately covers the
    even-count boundary case explicitly."""
    return raw_dataframe.head(401).reset_index(drop=True)
