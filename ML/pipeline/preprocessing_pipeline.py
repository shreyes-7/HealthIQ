"""The single, reusable, end-to-end preprocessing pipeline for the NHAMCS
ED admission dataset: load -> validate -> clean -> engineer features
(encode + scale), with survey design variables preserved untouched
throughout.

This module exists because CLAUDE.md and PROJECT_CONTEXT.md both require
that "preprocessing during inference must exactly match preprocessing
during training." Milestones 3 and 4 built the individual cleaning and
feature-engineering stages; this module is what actually enforces that
requirement, by giving both stages a fit/transform contract and gluing
them together behind one class:

    pipeline = PreprocessingPipeline()
    result = pipeline.fit_transform(raw_training_dataframe)   # learns everything
    pipeline.save(SAVED_MODELS_DIR)

    ...later, or in the backend at inference time...

    pipeline = PreprocessingPipeline.load(SAVED_MODELS_DIR)
    result = pipeline.transform(new_raw_dataframe)             # reuses learned state

`fit_transform` learns (and `transform` reuses without recomputing):
duplicate/constant/near-zero-variance columns to drop, which columns are
boolean, per-column imputation medians, and the fitted categorical
encoder and numerical scaler. Every other step (sentinel-code handling,
implied-decimal correction, text standardization, leakage exclusion,
target derivation) is a fixed, stateless rule and is safe to rerun on any
new data as-is.

The ML subsystem never trains a predictive model here -- only these
preprocessing artifacts (encoder, scaler, imputation values, dropped-
column lists) are fit and persisted, per Module 3/backend separation of
concerns in PROJECT_CONTEXT.md.
"""

from pathlib import Path

import joblib
import pandas as pd

from ML.cleaning.pipeline import fit_clean_dataset, transform_clean_dataset
from ML.feature_engineering.pipeline import fit_engineer_features, transform_engineer_features
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config
from ML.ingestion.loader import load_dataset
from ML.ingestion.validator import run_all_validations

PIPELINE_ARTIFACT_FILENAME = "preprocessing_pipeline.pkl"


class PreprocessingPipeline:
    """Reusable, fit/transform preprocessing pipeline.

    Each stage (cleaning, feature engineering) is a separate, independently
    testable module under ML/cleaning/ and ML/feature_engineering/; this
    class only orchestrates them in a fixed order and carries the fitted
    state between fit_transform() and transform() calls.
    """

    def __init__(self):
        self._cleaning_state = None
        self._feature_state = None
        self.is_fitted = False

    def fit_transform(self, raw_dataframe: pd.DataFrame) -> dict:
        """Learns all cleaning/encoding/scaling state from raw_dataframe
        and applies it, returning target/features/survey/identifiers."""
        cleaned, cleaning_log, cleaning_state = fit_clean_dataset(raw_dataframe)
        engineered = fit_engineer_features(cleaned)

        self._cleaning_state = cleaning_state
        self._feature_state = engineered["fitted_state"]
        self.is_fitted = True

        return {
            "target": engineered["target"],
            "features": engineered["features"],
            "survey": engineered["survey"],
            "identifiers": engineered["identifiers"],
            "cleaning_log": cleaning_log,
            "feature_log": engineered["log"],
        }

    def transform(self, raw_dataframe: pd.DataFrame) -> dict:
        """Applies previously-learned state to new raw data (a held-out
        split, or a future inference batch). Must be called after
        fit_transform() (or after load())."""
        if not self.is_fitted:
            raise RuntimeError("PreprocessingPipeline.transform() called before fit_transform()/load().")

        cleaned, cleaning_log = transform_clean_dataset(raw_dataframe, self._cleaning_state)
        engineered = transform_engineer_features(cleaned, self._feature_state)

        return {
            "target": engineered["target"],
            "features": engineered["features"],
            "survey": engineered["survey"],
            "identifiers": engineered["identifiers"],
            "cleaning_log": cleaning_log,
            "feature_log": engineered["log"],
        }

    @property
    def encoder(self):
        return self._feature_state["encoder"] if self._feature_state else None

    @property
    def scaler(self):
        return self._feature_state["scaler"] if self._feature_state else None

    def get_feature_names(self) -> list[str]:
        if not self.is_fitted:
            raise RuntimeError("PreprocessingPipeline is not fitted yet.")
        encoder_columns = [
            f"{column}__{category}"
            for column, categories in self.encoder.one_hot_categories_.items()
            for category in categories
        ] + [f"{column}__frequency" for column in self.encoder.frequency_maps_]
        return list(self._feature_state["continuous_columns"]) + encoder_columns

    def save(self, directory: Path) -> Path:
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        artifact_path = directory / PIPELINE_ARTIFACT_FILENAME
        joblib.dump(self, artifact_path)
        return artifact_path

    @classmethod
    def load(cls, directory: Path) -> "PreprocessingPipeline":
        return joblib.load(Path(directory) / PIPELINE_ARTIFACT_FILENAME)


def load_validate_and_fit(config_path: Path = DEFAULT_CONFIG_PATH) -> tuple[PreprocessingPipeline, dict]:
    """Convenience entry point matching this milestone's literal
    requirement list: load raw data, validate it, then fit the pipeline.
    Raises if validation fails rather than silently preprocessing bad
    data."""
    config = load_config(config_path)
    dataframe, _metadata = load_dataset(config)

    validation_checks = run_all_validations(dataframe, config)
    failed_checks = [check.name for check in validation_checks if not check.passed]
    if failed_checks:
        raise ValueError(f"Dataset validation failed: {failed_checks}")

    pipeline = PreprocessingPipeline()
    result = pipeline.fit_transform(dataframe)
    return pipeline, result
