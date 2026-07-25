"""Sprint 3 Milestone 6: Cohort Analysis.

Compares SHAP-based explanations across patient subgroups: does the
model lean on the same features for every cohort, or does its reasoning
shift for e.g. older patients vs. younger ones?

Cohort variables (age group, gender, arrival mode, triage level) were
one-hot encoded by Sprint 1's feature engineering, so raw categories must
be reconstructed from their dummy columns before grouping -- this module
does that generically from the encoder's own saved metadata (which
records each variable's dropped reference category), rather than
hand-listing categories per variable.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ML.explainability.shap_utils import mean_absolute_shap_by_source_variable, sigmoid


def reconstruct_categorical_from_onehot(features: pd.DataFrame, source_variable: str, encoder_metadata: dict) -> pd.Series:
    """Reconstructs the raw category per row from its one-hot dummy
    columns (e.g. "SEX__2") plus the encoder's recorded reference
    category (the category with no dummy column, dropped to avoid the
    dummy-variable trap during encoding)."""
    variable_metadata = encoder_metadata[source_variable]
    reference_category = variable_metadata["reference_category"]
    encoded_categories = variable_metadata["encoded_categories"]

    result = pd.Series(reference_category, index=features.index, dtype="object")
    for category in encoded_categories:
        dummy_column = f"{source_variable}__{category}"
        if dummy_column in features.columns:
            result.loc[features[dummy_column] == 1] = category

    return result


def compare_cohorts(
    shap_values: np.ndarray, feature_names: list[str], cohort_labels: pd.Series, expected_value: float, top_n: int = 10
) -> dict:
    """For each cohort group: top source variables by mean |SHAP|, and
    predicted-probability distribution summary."""
    margin_predictions = shap_values.sum(axis=1) + expected_value
    probabilities = sigmoid(margin_predictions)

    results = {}
    for group_value in sorted(cohort_labels.dropna().unique(), key=str):
        group_mask = (cohort_labels == group_value).values
        group_size = int(group_mask.sum())
        if group_size == 0:
            continue

        group_shap = shap_values[group_mask]
        group_probabilities = probabilities[group_mask]

        ranking = mean_absolute_shap_by_source_variable(group_shap, feature_names)
        results[str(group_value)] = {
            "n": group_size,
            "mean_predicted_probability": float(group_probabilities.mean()),
            "top_features": ranking.head(top_n).to_dict(),
        }

    return results


def plot_shap_distribution_by_cohort(shap_values: np.ndarray, cohort_labels: pd.Series, output_path, title: str) -> None:
    """Boxplot of each row's total SHAP magnitude (sum of |SHAP| across
    all features -- a per-row 'how much evidence pushed this prediction
    away from baseline' summary), grouped by cohort."""
    total_abs_shap_per_row = np.abs(shap_values).sum(axis=1)
    groups = sorted(cohort_labels.dropna().unique(), key=str)
    data = [total_abs_shap_per_row[(cohort_labels == group).values] for group in groups]

    figure, axis = plt.subplots(figsize=(8, 5))
    axis.boxplot(data, tick_labels=[str(group) for group in groups], showfliers=False)
    axis.set_ylabel("Total |SHAP| per row (sum across all features)")
    axis.set_title(title)
    plt.setp(axis.get_xticklabels(), rotation=30, ha="right")
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)
