"""Shared utilities for working with SHAP output: probability-space
conversion, tidy per-row/per-feature views, and source-variable
aggregation (mirrors the same aggregation done for tree importance in
Sprint 2's feature selection, for the same reason -- one-hot encoding
splits a single source variable across several dummy columns).
"""

import numpy as np
import pandas as pd


def sigmoid(margin_values):
    """Converts margin (log-odds) values to probability space."""
    return 1.0 / (1.0 + np.exp(-np.asarray(margin_values)))


def source_variable_name(encoded_feature_name: str) -> str:
    """Maps an encoded feature name (e.g. "SEX__2", "DIAG1__frequency")
    back to its source variable, matching
    ML.feature_engineering.feature_selection.source_variable_name."""
    return encoded_feature_name.split("__", 1)[0]


def mean_absolute_shap_by_feature(shap_values: np.ndarray, feature_names: list[str]) -> pd.Series:
    """Global importance: mean |SHAP value| per feature, across all
    explained rows. Standard SHAP global-importance definition."""
    mean_abs = np.abs(shap_values).mean(axis=0)
    return pd.Series(mean_abs, index=feature_names, name="mean_abs_shap").sort_values(ascending=False)


def mean_absolute_shap_by_source_variable(shap_values: np.ndarray, feature_names: list[str]) -> pd.Series:
    """Same as above, but summed back to each source variable -- the
    clinically interpretable view, since a single variable like AGE_GROUP
    is split across several one-hot dummy columns."""
    per_feature = mean_absolute_shap_by_feature(shap_values, feature_names)
    per_feature_df = per_feature.reset_index()
    per_feature_df.columns = ["feature", "mean_abs_shap"]
    per_feature_df["source_variable"] = per_feature_df["feature"].map(source_variable_name)
    return per_feature_df.groupby("source_variable")["mean_abs_shap"].sum().sort_values(ascending=False)


def row_explanation(
    shap_values_row: np.ndarray, feature_values_row: pd.Series, feature_names: list[str], expected_value: float, top_n: int = 15
) -> dict:
    """Builds a JSON-ready explanation for one row: predicted probability,
    base rate, and the top contributing features ranked by |SHAP value|,
    each with its raw feature value and probability-space contribution."""
    margin_prediction = float(shap_values_row.sum() + expected_value)

    contributions = pd.DataFrame(
        {
            "feature": feature_names,
            "feature_value": feature_values_row.values,
            "shap_value_margin": shap_values_row,
        }
    )
    contributions["source_variable"] = contributions["feature"].map(source_variable_name)
    contributions["abs_shap_value_margin"] = contributions["shap_value_margin"].abs()
    contributions = contributions.sort_values("abs_shap_value_margin", ascending=False)

    return {
        "predicted_probability": float(sigmoid(margin_prediction)),
        "base_rate_probability": float(sigmoid(expected_value)),
        "top_contributing_features": contributions.head(top_n)[
            ["feature", "source_variable", "feature_value", "shap_value_margin"]
        ].to_dict(orient="records"),
    }
