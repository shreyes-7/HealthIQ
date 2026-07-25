"""Sprint 3 Milestone 4: Local Explainability.

Explains three genuinely different patient cases (not three easy wins):
a confident correct admission, a confident correct discharge, and the
model's most uncertain (borderline) prediction -- selected programmatically
from the validation split, not hand-picked.

No model is retrained here -- reuses the SHAP values from Milestone 2.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_local_explainability
"""

import json
import logging
from datetime import datetime, timezone

import numpy as np

from ML.explainability.artifacts import load_feature_names, load_split, split_features_and_target
from ML.explainability.local_explanations import (
    explain_patient_in_words,
    plot_decision,
    plot_force,
    plot_waterfall,
    select_representative_patients,
)
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
PATIENT_EXPLANATIONS_DIR = EXPLAINABILITY_REPORTS_DIR / "patient_explanations"


def get_expected_value() -> float:
    import joblib

    explainer = joblib.load(resolve_repo_path("ML/saved_models/shap_explainer.pkl"))
    return float(np.asarray(explainer.expected_value).reshape(-1)[0])


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 4 - Local Explainability")

    feature_names = load_feature_names()
    shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")
    validation_split = load_split("validation")
    validation_features, validation_target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names].reset_index(drop=True)
    validation_target = validation_target.reset_index(drop=True)

    expected_value = get_expected_value()
    selection = select_representative_patients(shap_values, validation_target, expected_value)

    for patient_key in ("patient_1_confident_admission", "patient_2_confident_discharge", "patient_3_borderline"):
        info = selection[patient_key]
        row_index = info["row_index"]
        patient_dir = PATIENT_EXPLANATIONS_DIR / f"patient_{patient_key.split('_')[1]}"
        patient_dir.mkdir(parents=True, exist_ok=True)

        shap_row = shap_values[row_index]
        features_row = validation_features.iloc[row_index]
        actual_label = int(validation_target.iloc[row_index])

        plot_waterfall(shap_row, features_row, feature_names, expected_value, patient_dir / "waterfall_plot.png")
        plot_force(shap_row, features_row, feature_names, expected_value, patient_dir / "force_plot.png")
        plot_decision(shap_row, features_row, feature_names, expected_value, patient_dir / "decision_plot.png")

        explanation = explain_patient_in_words(shap_row, features_row, feature_names, expected_value)
        explanation["row_index_in_validation_split"] = row_index
        explanation["actual_label"] = actual_label
        explanation["selection_reason"] = info["reason"]

        (patient_dir / "explanation.json").write_text(json.dumps(explanation, indent=2, default=str), encoding="utf-8")
        write_patient_report(patient_dir, patient_key, explanation)

        logger.info(
            "%s (row %d): predicted P(admit)=%.4f, actual=%s -- %s",
            patient_key, row_index, explanation["predicted_probability"],
            "admitted" if actual_label else "not admitted", "correct" if (explanation["predicted_admission"] == bool(actual_label)) else "MISCLASSIFIED",
        )

    logger.info("Sprint 3 Milestone 4 (Local Explainability) completed successfully.")


def write_patient_report(patient_dir, patient_key: str, explanation: dict) -> None:
    lines = [
        f"# Patient Explanation — {patient_key}",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"**Selection reason**: {explanation['selection_reason']}",
        "",
        f"- Row index in validation split: {explanation['row_index_in_validation_split']}",
        f"- Predicted probability of admission: **{explanation['predicted_probability']:.4f}**",
        f"- Base rate (population average) probability: {explanation['base_rate_probability']:.4f}",
        f"- Predicted outcome: {'ADMITTED' if explanation['predicted_admission'] else 'NOT ADMITTED'}",
        f"- Actual outcome: {'ADMITTED' if explanation['actual_label'] else 'NOT ADMITTED'}",
        f"- Prediction was: {'CORRECT' if explanation['predicted_admission'] == bool(explanation['actual_label']) else '**MISCLASSIFIED**'}",
        "",
        "## Variables That Increased Admission Risk",
        "",
        "| Feature | Source Variable | Value | SHAP (margin) |",
        "|---|---|---|---|",
    ]
    for item in explanation["features_that_increased_risk"]:
        lines.append(f"| `{item['feature']}` | `{item['source_variable']}` | {item['feature_value']} | +{item['shap_value']:.4f} |")

    lines += ["", "## Variables That Decreased Admission Risk", "", "| Feature | Source Variable | Value | SHAP (margin) |", "|---|---|---|---|"]
    for item in explanation["features_that_decreased_risk"]:
        lines.append(f"| `{item['feature']}` | `{item['source_variable']}` | {item['feature_value']} | {item['shap_value']:.4f} |")

    lines += [
        "",
        "## Visualizations",
        "",
        "- `waterfall_plot.png` — step-by-step from base rate to final prediction",
        "- `force_plot.png` — same information, compact horizontal layout",
        "- `decision_plot.png` — cumulative path of the prediction across top features",
    ]

    (patient_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
