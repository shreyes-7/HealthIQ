"""Loads the raw NHAMCS SAS dataset. Read-only: never modifies the raw file."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
import pyreadstat

from ML.ingestion.config import resolve_repo_path

logger = logging.getLogger(__name__)


def get_raw_dataset_path(config: dict) -> Path:
    """Resolve the raw dataset path declared in the configuration."""
    return resolve_repo_path(config["dataset"]["raw_path"])


def verify_raw_dataset_exists(config: dict) -> Path:
    """Confirm the raw dataset file exists before any read is attempted."""
    dataset_path = get_raw_dataset_path(config)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {dataset_path}")

    logger.info("Raw dataset located at %s", dataset_path)
    return dataset_path


def load_dataset_metadata(config: dict) -> Any:
    """Read only the SAS file metadata (labels, dimensions), without row data."""
    dataset_path = verify_raw_dataset_exists(config)
    logger.info("Reading dataset metadata from %s", dataset_path)

    _, metadata = pyreadstat.read_sas7bdat(str(dataset_path), metadataonly=True)
    return metadata


def load_dataset(config: dict) -> tuple[pd.DataFrame, Any]:
    """Load the full raw dataset into memory as (dataframe, metadata)."""
    dataset_path = verify_raw_dataset_exists(config)
    logger.info("Loading full dataset from %s", dataset_path)

    dataframe, metadata = pyreadstat.read_sas7bdat(str(dataset_path))
    logger.info("Loaded dataset with shape %s", dataframe.shape)
    return dataframe, metadata
