"""Sprint 3 Milestone 7: Explanation Validation.

Verifies the explanations produced by Milestones 2-6 are actually
trustworthy, not just present. SHAP values are only useful if they
genuinely reconstruct the model's predictions, stay ordered consistently
with the features, and are reproducible -- none of that is guaranteed
just because the plotting code ran without an exception.
"""

import numpy as np
import pandas as pd

from ML.explainability.explainer import compute_shap_values
from ML.explainability.shap_utils import sigmoid

RECONSTRUCTION_TOLERANCE = 1e-6


def verify_shap_reproduces_predictions(
    shap_values: np.ndarray, expected_value: float, model, features: pd.DataFrame
) -> dict:
    """The single most important correctness check: does
    sigmoid(sum(shap_values) + expected_value) equal predict_proba? If
    not, the explanations don't actually describe this model's behavior."""
    reconstructed_margin = shap_values.sum(axis=1) + expected_value
    reconstructed_probability = sigmoid(reconstructed_margin)
    actual_probability = model.predict_proba(features)[:, 1]

    max_abs_diff = float(np.max(np.abs(reconstructed_probability - actual_probability)))
    passed = max_abs_diff < RECONSTRUCTION_TOLERANCE

    return {
        "check": "shap_values_reproduce_predictions",
        "passed": passed,
        "max_abs_diff": max_abs_diff,
        "tolerance": RECONSTRUCTION_TOLERANCE,
        "n_rows_checked": len(features),
    }


def verify_feature_ordering_consistency(shap_values: np.ndarray, feature_names: list[str], features: pd.DataFrame) -> dict:
    shape_matches = shap_values.shape[1] == len(feature_names)
    columns_match = list(features.columns) == feature_names
    return {
        "check": "feature_ordering_consistency",
        "passed": bool(shape_matches and columns_match),
        "shap_values_column_count": shap_values.shape[1],
        "feature_names_count": len(feature_names),
        "features_dataframe_order_matches": columns_match,
    }


def verify_explanation_stability(explainer, features: pd.DataFrame, sample_size: int = 100) -> dict:
    """TreeExplainer's default (tree_path_dependent) algorithm is exact
    and deterministic -- no sampling involved -- so recomputing SHAP
    values for the same rows should be bit-identical, not just close.
    A real difference here would indicate a non-deterministic explainer
    configuration, which would undermine every plot and report already
    generated."""
    sample = features.head(sample_size)
    first_run = compute_shap_values(explainer, sample)
    second_run = compute_shap_values(explainer, sample)

    max_abs_diff = float(np.max(np.abs(first_run - second_run)))
    return {
        "check": "explanation_stability",
        "passed": max_abs_diff == 0.0,
        "max_abs_diff_between_two_runs": max_abs_diff,
        "n_rows_checked": sample_size,
    }


def verify_no_preprocessing_mismatch(pipeline, model, feature_names: list[str], raw_sample: pd.DataFrame) -> dict:
    """Runs raw data through the Sprint 1 pipeline fresh and confirms its
    output feature schema exactly matches what the model (and therefore
    the SHAP explainer, which was built directly on the model) expects."""
    result = pipeline.transform(raw_sample)
    schema_matches = list(result["features"].columns) == feature_names

    predict_ok = False
    if schema_matches:
        try:
            predictions = model.predict_proba(result["features"])[:, 1]
            predict_ok = len(predictions) == len(raw_sample) and not np.isnan(predictions).any()
        except Exception:
            predict_ok = False

    return {
        "check": "no_preprocessing_mismatch",
        "passed": bool(schema_matches and predict_ok),
        "schema_matches": schema_matches,
        "model_predicts_successfully": predict_ok,
        "n_rows_checked": len(raw_sample),
    }


def verify_no_missing_shap_values(shap_values: np.ndarray) -> dict:
    nan_count = int(np.isnan(shap_values).sum())
    return {
        "check": "no_missing_shap_values",
        "passed": nan_count == 0,
        "nan_count": nan_count,
        "total_values": int(shap_values.size),
    }
