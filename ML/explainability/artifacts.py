"""Loads the artifacts every Sprint 3 (Explainable AI) milestone depends
on: the fitted preprocessing pipeline, the selected model, feature
metadata, and the train/validation/test splits.

Centralized here so every explainability script loads these identically
instead of re-implementing path/loading logic per script -- the same
pattern used by ML/ingestion, ML/cleaning, etc. in earlier sprints.
"""

import json

import joblib
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path

SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
PROCESSED_DATA_DIR = resolve_repo_path("Data/processed")

# Same non-feature set used throughout Sprint 2 (target + survey design
# variables, preserved but never fed to the model, + identifiers).
NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}


def load_model():
    """Loads the Sprint 2 selected model (LightGBM), never retrains it."""
    return joblib.load(SAVED_MODELS_DIR / "model.pkl")


def load_model_metadata() -> dict:
    return json.loads((SAVED_MODELS_DIR / "model_metadata.json").read_text(encoding="utf-8"))


def load_feature_names() -> list[str]:
    return json.loads((SAVED_MODELS_DIR / "feature_names.json").read_text(encoding="utf-8"))


def load_preprocessing_pipeline():
    """Loads the Sprint 1 PreprocessingPipeline, fit on the training split only."""
    from ML.pipeline.preprocessing_pipeline import PreprocessingPipeline

    return PreprocessingPipeline.load(SAVED_MODELS_DIR)


def load_shap_explainer():
    """Loads the Sprint 3 Milestone 2 fitted SHAP explainer -- never
    rebuilds it, so every consumer explains with the exact same
    explainer that was validated in Milestone 7."""
    return joblib.load(SAVED_MODELS_DIR / "shap_explainer.pkl")


def load_shap_expected_value() -> float:
    import numpy as np

    explainer = load_shap_explainer()
    return float(np.asarray(explainer.expected_value).reshape(-1)[0])


def load_split(name: str) -> pd.DataFrame:
    """name is one of 'train', 'validation', 'test'."""
    return pd.read_parquet(PROCESSED_DATA_DIR / f"{name}.parquet")


def split_features_and_target(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    feature_columns = [column for column in dataframe.columns if column not in NON_FEATURE_COLUMNS]
    return dataframe[feature_columns], dataframe[TARGET_COLUMN_NAME]
