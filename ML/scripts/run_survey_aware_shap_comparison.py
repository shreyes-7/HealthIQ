"""Survey-Aware Deep Dive, Step 2: SHAP comparison between the
survey-weighted and unweighted LightGBM models.

Reuses the already-computed, already-validated unweighted SHAP values
from Sprint 3 Milestone 2/7 rather than recomputing them. Computes SHAP
values for the weighted model fresh (Step 1's new artifact), using the
exact same TreeExplainer approach.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_survey_aware_shap_comparison
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ML.explainability.artifacts import load_feature_names, load_shap_expected_value, load_split, split_features_and_target
from ML.explainability.explainer import build_explainer, compute_shap_values
from ML.explainability.local_explanations import explain_patient_in_words
from ML.explainability.shap_utils import sigmoid
from ML.explainability.survey_aware_shap import compare_importance_rankings
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
DEEP_DIVE_DIR = resolve_repo_path("ML/reports/survey_aware_deep_dive")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
DATA_DICTIONARY_PATH = resolve_repo_path("ML/reports/data_dictionary.csv")

PATIENT_ROW_INDICES = {"patient_1": 1809, "patient_2": 1219, "patient_3": 2213}


def main() -> None:
    logger.info("Starting Survey-Aware Deep Dive Step 2: SHAP Comparison")
    DEEP_DIVE_DIR.mkdir(parents=True, exist_ok=True)

    feature_names = load_feature_names()
    unweighted_shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")
    unweighted_expected_value = load_shap_expected_value()

    weighted_model = joblib.load(SAVED_MODELS_DIR / "model_survey_weighted.pkl")
    weighted_explainer = build_explainer(weighted_model)
    weighted_expected_value = float(np.asarray(weighted_explainer.expected_value).reshape(-1)[0])

    validation_split = load_split("validation")
    validation_features, _target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names].reset_index(drop=True)

    logger.info("Computing SHAP values for the survey-weighted model on the validation split")
    weighted_shap_values = compute_shap_values(weighted_explainer, validation_features)
    np.save(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation_weighted.npy", weighted_shap_values)

    comparison = compare_importance_rankings(unweighted_shap_values, weighted_shap_values, feature_names)
    logger.info(
        "Spearman rank correlation (top source variables): %.4f (p=%.4g), top-20 overlap: %d/20",
        comparison["spearman_rank_correlation"], comparison["spearman_p_value"], comparison["top_n_overlap_count"],
    )

    # Systematic check across the FULL validation split: how often does
    # survey weighting flip the predicted decision, not just for the 3
    # hand-examined patients?
    unweighted_probabilities = sigmoid(unweighted_shap_values.sum(axis=1) + unweighted_expected_value)
    weighted_probabilities = sigmoid(weighted_shap_values.sum(axis=1) + weighted_expected_value)
    decision_flips = (unweighted_probabilities >= 0.5) != (weighted_probabilities >= 0.5)
    flip_rate = float(decision_flips.mean())
    logger.info(
        "Decision-flip rate across full validation split: %d/%d (%.2f%%)",
        int(decision_flips.sum()), len(decision_flips), flip_rate * 100,
    )

    plot_ranking_comparison(comparison, DEEP_DIVE_DIR / "figures" / "weighted_vs_unweighted_importance.png")

    patient_comparisons = {}
    for patient_key, row_index in PATIENT_ROW_INDICES.items():
        unweighted_explanation = explain_patient_in_words(
            unweighted_shap_values[row_index], validation_features.iloc[row_index], feature_names, unweighted_expected_value
        )
        weighted_explanation = explain_patient_in_words(
            weighted_shap_values[row_index], validation_features.iloc[row_index], feature_names, weighted_expected_value
        )
        patient_comparisons[patient_key] = {
            "row_index": row_index,
            "unweighted_probability": unweighted_explanation["predicted_probability"],
            "weighted_probability": weighted_explanation["predicted_probability"],
            "unweighted_top_feature": unweighted_explanation["features_that_increased_risk"][0]["feature"]
            if unweighted_explanation["features_that_increased_risk"] else None,
            "weighted_top_feature": weighted_explanation["features_that_increased_risk"][0]["feature"]
            if weighted_explanation["features_that_increased_risk"] else None,
        }
        logger.info(
            "%s: unweighted P(admit)=%.4f, weighted P(admit)=%.4f",
            patient_key, unweighted_explanation["predicted_probability"], weighted_explanation["predicted_probability"],
        )

    # Among flipped decisions, how close to the boundary was the unweighted
    # prediction? Confirms (or refutes) that flips concentrate near 0.5.
    flipped_unweighted_distance_from_boundary = np.abs(unweighted_probabilities[decision_flips] - 0.5)
    not_flipped_unweighted_distance_from_boundary = np.abs(unweighted_probabilities[~decision_flips] - 0.5)
    flip_stats = {
        "flip_count": int(decision_flips.sum()),
        "total": int(len(decision_flips)),
        "flip_rate": flip_rate,
        "mean_distance_from_boundary_when_flipped": float(flipped_unweighted_distance_from_boundary.mean()) if decision_flips.any() else None,
        "mean_distance_from_boundary_when_not_flipped": float(not_flipped_unweighted_distance_from_boundary.mean()),
    }

    (DEEP_DIVE_DIR / "shap_comparison.json").write_text(
        json.dumps(
            {"ranking_comparison": comparison, "patient_comparisons": patient_comparisons, "decision_flip_stats": flip_stats},
            indent=2, default=str,
        ),
        encoding="utf-8",
    )

    write_report(comparison, patient_comparisons, flip_stats)
    logger.info("Survey-Aware Deep Dive Step 2 completed successfully.")


def plot_ranking_comparison(comparison: dict, output_path) -> None:
    unweighted = pd.Series(comparison["unweighted_ranking"])
    weighted = pd.Series(comparison["weighted_ranking"]).reindex(unweighted.index)

    figure, axis = plt.subplots(figsize=(9, 8))
    y_positions = np.arange(len(unweighted))
    axis.barh(y_positions - 0.2, unweighted.values, height=0.4, label="Unweighted (production)", color="#1f77b4")
    axis.barh(y_positions + 0.2, weighted.values, height=0.4, label="Survey-weighted", color="#d62728")
    axis.set_yticks(y_positions)
    axis.set_yticklabels(unweighted.index)
    axis.invert_yaxis()
    axis.set_xlabel("Mean |SHAP value|")
    axis.set_title("Global Feature Importance: Weighted vs. Unweighted LightGBM")
    axis.legend()
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def write_report(comparison: dict, patient_comparisons: dict, flip_stats: dict) -> None:
    labels = {}
    if DATA_DICTIONARY_PATH.exists():
        data_dictionary = pd.read_csv(DATA_DICTIONARY_PATH)
        labels = dict(zip(data_dictionary["variable_name"], data_dictionary["label"]))

    lines = [
        "# SHAP Comparison: Survey-Weighted vs. Unweighted LightGBM",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Answers Sprint 3's open 'Future Work' item: do SHAP-based explanations differ "
        "meaningfully between a weighted and unweighted model? Both SHAP value sets are "
        "computed with `TreeExplainer` on the identical validation split.",
        "",
        f"**Spearman rank correlation between the two importance rankings: "
        f"{comparison['spearman_rank_correlation']:.4f}** (p={comparison['spearman_p_value']:.4g}). "
        f"Top-20 overlap: {comparison['top_n_overlap_count']}/20 variables.",
        "",
    ]

    if comparison["only_in_unweighted_top_n"] or comparison["only_in_weighted_top_n"]:
        lines.append("Variables that entered or dropped out of the top 20 under weighting:")
        lines.append("")
        if comparison["only_in_unweighted_top_n"]:
            lines.append(f"- Only in unweighted top 20: {comparison['only_in_unweighted_top_n']}")
        if comparison["only_in_weighted_top_n"]:
            lines.append(f"- Only in weighted top 20: {comparison['only_in_weighted_top_n']}")
        lines.append("")

    lines += [
        "![Weighted vs Unweighted Importance](figures/weighted_vs_unweighted_importance.png)",
        "",
        "## Decision-Flip Rate (full validation split, not just the 3 examined patients)",
        "",
        f"Across all {flip_stats['total']} validation visits: survey weighting flips the predicted "
        f"decision (crosses the 0.5 threshold) for **{flip_stats['flip_count']} visits "
        f"({flip_stats['flip_rate']*100:.2f}%)**.",
        "",
    ]
    if flip_stats["mean_distance_from_boundary_when_flipped"] is not None:
        lines.append(
            f"- Mean distance from the 0.5 boundary (unweighted prediction) for flipped cases: "
            f"{flip_stats['mean_distance_from_boundary_when_flipped']:.4f}"
        )
    else:
        lines.append("- No decisions flipped.")
    lines.append(
        f"- Mean distance from the 0.5 boundary for non-flipped cases: "
        f"{flip_stats['mean_distance_from_boundary_when_not_flipped']:.4f}"
    )
    lines += [
        "",
        "If the first number is much smaller than the second, flips concentrate near the decision "
        "boundary exactly as the patient_3 example suggests, confirming it generalizes rather than "
        "being a one-off coincidence.",
        "",
        "## Per-Patient Comparison",
        "",
        "The same 3 patients examined in Sprint 3 Milestone 4, now compared under both models.",
        "",
        "| Patient | Row | Unweighted P(admit) | Weighted P(admit) | Difference |",
        "|---|---|---|---|---|",
    ]
    for patient_key, data in patient_comparisons.items():
        diff = data["weighted_probability"] - data["unweighted_probability"]
        lines.append(
            f"| {patient_key} | {data['row_index']} | {data['unweighted_probability']:.4f} | "
            f"{data['weighted_probability']:.4f} | {diff:+.4f} |"
        )

    largest_shift_patient = max(patient_comparisons.items(), key=lambda item: abs(item[1]["weighted_probability"] - item[1]["unweighted_probability"]))
    largest_shift_key, largest_shift_data = largest_shift_patient
    crosses_threshold = (largest_shift_data["unweighted_probability"] >= 0.5) != (largest_shift_data["weighted_probability"] >= 0.5)

    lines += [
        "",
        "## Interpretation",
        "",
    ]
    if comparison["spearman_rank_correlation"] > 0.9:
        lines.append(
            f"A rank correlation of {comparison['spearman_rank_correlation']:.4f} is very high — "
            "survey weighting shifts the model's raw discrimination slightly (see "
            "`weighted_vs_unweighted_lightgbm.md`) but does **not** meaningfully change *which* "
            "features it relies on or in what order. The model's clinical reasoning is stable "
            "under survey weighting, even though its calibration to this specific sample shifts."
        )
    else:
        lines.append(
            f"A rank correlation of {comparison['spearman_rank_correlation']:.4f} indicates survey "
            "weighting meaningfully reshuffles which features the model relies on most — this is a "
            "substantive finding worth highlighting, not just a calibration footnote."
        )

    lines.append("")
    if crosses_threshold:
        lines.append(
            f"**The most clinically significant finding here**: `{largest_shift_key}` "
            f"(the borderline case from Sprint 3, originally predicted at P={largest_shift_data['unweighted_probability']:.4f}) "
            f"shifts to P={largest_shift_data['weighted_probability']:.4f} under survey weighting — "
            "**crossing the 0.5 decision threshold**, flipping the predicted outcome entirely. "
            "Confident predictions (`patient_1`, `patient_2`) barely move at all. This shows "
            "survey weighting's practical effect concentrates exactly where it matters most "
            "clinically: borderline cases, where the admission decision is already genuinely "
            "uncertain, are the ones most sensitive to whether the model accounts for the "
            "survey's sampling design."
        )
    else:
        lines.append(
            f"The largest single-patient shift was `{largest_shift_key}` "
            f"({largest_shift_data['unweighted_probability']:.4f} → {largest_shift_data['weighted_probability']:.4f}), "
            "which did not cross the 0.5 decision threshold in this sample of 3 — worth checking "
            "across a larger sample if a threshold-crossing rate estimate is needed."
        )

    report_path = DEEP_DIVE_DIR / "shap_comparison_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
