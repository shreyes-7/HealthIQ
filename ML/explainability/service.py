"""Sprint 3 Milestone 8: Explanation Generator, Global/Local Explanation
Services.

The backend-facing API surface for the next sprint's FastAPI integration:
given a single patient record (new, not necessarily in any existing
split), runs it through the exact same Sprint 1 PreprocessingPipeline and
Sprint 3 SHAP explainer already validated in Milestone 7, and returns a
JSON-serializable explanation. Global explanations are served from
Milestone 3's precomputed artifacts rather than recomputed per request --
global importance is a property of the whole validation set, not
something that changes per API call.
"""

import numpy as np
import pandas as pd

from ML.explainability.artifacts import (
    load_feature_names,
    load_model,
    load_preprocessing_pipeline,
    load_shap_expected_value,
    load_shap_explainer,
    load_split,
    split_features_and_target,
)
from ML.explainability.explainer import compute_shap_values
from ML.explainability.local_explanations import explain_patient_in_words
from ML.explainability.shap_utils import mean_absolute_shap_by_feature, mean_absolute_shap_by_source_variable
from ML.ingestion.config import resolve_repo_path

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")


class ExplanationService:
    """Loads every artifact ONCE (model, pipeline, explainer, feature
    names) and reuses them for every explanation request -- mirrors how
    a backend process should hold these in memory rather than reloading
    per request (PROJECT_CONTEXT.md: "Model artifacts should be loaded
    only once whenever possible"). Never retrains or refits anything."""

    def __init__(self):
        self.model = load_model()
        self.pipeline = load_preprocessing_pipeline()
        self.explainer = load_shap_explainer()
        self.feature_names = load_feature_names()
        self.expected_value = load_shap_expected_value()

    def explain_patient(self, raw_patient_record: pd.DataFrame) -> dict:
        """raw_patient_record: a DataFrame with the same raw NHAMCS
        columns as the raw dataset (one or more rows, e.g. a single-row
        DataFrame for a true single-patient API request). Returns a
        plain-language explanation for the first row."""
        result = self.pipeline.transform(raw_patient_record)
        features = result["features"][self.feature_names]

        shap_values = compute_shap_values(self.explainer, features)
        return explain_patient_in_words(shap_values[0], features.iloc[0], self.feature_names, self.expected_value)

    def explain_by_split_row(self, split_name: str, row_index: int) -> dict:
        """Convenience for testing/demos: explain a row already in
        train/validation/test by index, using the already-cleaned split
        (no raw -> pipeline round trip needed)."""
        split = load_split(split_name)
        features, _target = split_features_and_target(split)
        features = features[self.feature_names].reset_index(drop=True)

        shap_values = compute_shap_values(self.explainer, features.iloc[[row_index]])
        return explain_patient_in_words(
            shap_values[0], features.iloc[row_index], self.feature_names, self.expected_value
        )


def get_global_explanation(top_n: int = 20) -> dict:
    """Serves Milestone 3's precomputed global importance -- does not
    recompute SHAP values."""
    feature_names = load_feature_names()
    shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")

    per_feature = mean_absolute_shap_by_feature(shap_values, feature_names)
    per_source_variable = mean_absolute_shap_by_source_variable(shap_values, feature_names)

    return {
        "top_features": per_feature.head(top_n).to_dict(),
        "top_source_variables": per_source_variable.head(top_n).to_dict(),
        "computed_on": "validation_split",
        "n_rows": int(shap_values.shape[0]),
    }
