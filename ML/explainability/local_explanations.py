"""Sprint 3 Milestone 4: Local Explainability.

Explains individual predictions: why a specific patient's predicted risk
came out the way it did, which variables pushed it up, and which pushed
it down.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from ML.explainability.shap_utils import sigmoid, source_variable_name

WATERFALL_MAX_DISPLAY = 15
DECISION_PLOT_TOP_N_FOR_CONTEXT = 20


def select_representative_patients(shap_values: np.ndarray, target: pd.Series, expected_value: float) -> dict:
    """Selects three genuinely different cases rather than three easy wins:
    a confident correct admission prediction, a confident correct
    non-admission prediction, and the most uncertain (borderline)
    prediction in the explained set -- the most instructive case for
    understanding where the model is unsure."""
    margin_predictions = shap_values.sum(axis=1) + expected_value
    probabilities = sigmoid(margin_predictions)
    target_values = target.reset_index(drop=True)

    admitted_mask = target_values == 1
    not_admitted_mask = target_values == 0

    confident_admission_index = probabilities[admitted_mask.values].argmax()
    confident_admission_index = target_values[admitted_mask].index[confident_admission_index]

    confident_discharge_index = probabilities[not_admitted_mask.values].argmin()
    confident_discharge_index = target_values[not_admitted_mask].index[confident_discharge_index]

    borderline_index = int(np.argmin(np.abs(probabilities - 0.5)))

    return {
        "patient_1_confident_admission": {
            "row_index": int(confident_admission_index),
            "reason": "Highest-confidence correctly-predicted admission -- the clearest positive case.",
        },
        "patient_2_confident_discharge": {
            "row_index": int(confident_discharge_index),
            "reason": "Lowest-confidence-of-admission correctly-predicted discharge -- the clearest negative case.",
        },
        "patient_3_borderline": {
            "row_index": borderline_index,
            "reason": "Predicted probability closest to 0.5 -- the model's most uncertain case, most "
            "informative for understanding where evidence conflicts.",
        },
        "probabilities": probabilities,
    }


def plot_waterfall(shap_values_row: np.ndarray, feature_values_row: pd.Series, feature_names: list[str], expected_value: float, output_path) -> None:
    explanation = shap.Explanation(
        values=shap_values_row,
        base_values=expected_value,
        data=feature_values_row.values,
        feature_names=feature_names,
    )
    figure = plt.figure(figsize=(9, 7))
    shap.plots.waterfall(explanation, max_display=WATERFALL_MAX_DISPLAY, show=False)
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def plot_force(shap_values_row: np.ndarray, feature_values_row: pd.Series, feature_names: list[str], expected_value: float, output_path) -> None:
    shap.force_plot(
        expected_value, shap_values_row, feature_values_row, feature_names=feature_names, matplotlib=True, show=False,
    )
    figure = plt.gcf()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def plot_decision(shap_values_row: np.ndarray, feature_values_row: pd.Series, feature_names: list[str], expected_value: float, output_path) -> None:
    figure = plt.figure(figsize=(9, 8))
    shap.decision_plot(
        expected_value, shap_values_row, feature_values_row, feature_names=feature_names,
        feature_display_range=slice(-1, -DECISION_PLOT_TOP_N_FOR_CONTEXT - 1, -1), show=False,
    )
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def explain_patient_in_words(shap_values_row: np.ndarray, feature_values_row: pd.Series, feature_names: list[str], expected_value: float, top_n: int = 8) -> dict:
    """A plain-language explanation: predicted probability, and the top
    features that increased vs. decreased admission risk."""
    margin_prediction = float(shap_values_row.sum() + expected_value)
    predicted_probability = float(sigmoid(margin_prediction))

    contributions = pd.DataFrame(
        {"feature": feature_names, "feature_value": feature_values_row.values, "shap_value": shap_values_row}
    )
    contributions["source_variable"] = contributions["feature"].map(source_variable_name)

    increased_risk = contributions[contributions["shap_value"] > 0].sort_values("shap_value", ascending=False)
    decreased_risk = contributions[contributions["shap_value"] < 0].sort_values("shap_value", ascending=True)

    return {
        "predicted_probability": predicted_probability,
        "base_rate_probability": float(sigmoid(expected_value)),
        "predicted_admission": predicted_probability >= 0.5,
        "features_that_increased_risk": increased_risk.head(top_n)[
            ["feature", "source_variable", "feature_value", "shap_value"]
        ].to_dict(orient="records"),
        "features_that_decreased_risk": decreased_risk.head(top_n)[
            ["feature", "source_variable", "feature_value", "shap_value"]
        ].to_dict(orient="records"),
    }
