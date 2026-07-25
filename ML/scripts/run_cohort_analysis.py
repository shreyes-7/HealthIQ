"""Sprint 3 Milestone 6: Cohort Analysis.

Compares SHAP-based feature importance and prediction distributions
across 5 patient cohort dimensions: actual admission status, age group,
gender, arrival mode, and triage level. Cohort categories are
reconstructed from their one-hot encoded columns using the encoder's own
saved reference-category metadata (see ML.explainability.cohort), not
hand-listed.

No model is retrained here -- reuses the SHAP values from Milestone 2.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_cohort_analysis
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import numpy as np

from ML.explainability.artifacts import load_feature_names, load_split, split_features_and_target
from ML.explainability.cohort import compare_cohorts, plot_shap_distribution_by_cohort, reconstruct_categorical_from_onehot
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
COHORT_PLOTS_DIR = EXPLAINABILITY_REPORTS_DIR / "cohort_plots"
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")

# (cohort_name, source_variable_or_None). None means "use the actual target", not a
# one-hot-encoded feature -- ADMISSION_VS_DISCHARGE is handled specially in main().
COHORT_DIMENSIONS = [
    ("age_group", "AGE_GROUP"),
    ("gender", "SEX"),
    ("arrival_mode", "ARREMS"),
    ("triage_level", "IMMEDR"),
]


def get_expected_value() -> float:
    explainer = joblib.load(SAVED_MODELS_DIR / "shap_explainer.pkl")
    return float(np.asarray(explainer.expected_value).reshape(-1)[0])


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 6 - Cohort Analysis")
    COHORT_PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    feature_names = load_feature_names()
    shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")
    validation_split = load_split("validation")
    validation_features, validation_target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names].reset_index(drop=True)
    validation_target = validation_target.reset_index(drop=True)

    encoder_metadata = json.loads((SAVED_MODELS_DIR / "metadata.json").read_text())["encoder_feature_metadata"]
    expected_value = get_expected_value()

    all_results = {}

    admission_labels = validation_target.map({0: "not_admitted", 1: "admitted"})
    all_results["admission_vs_discharge"] = compare_cohorts(shap_values, feature_names, admission_labels, expected_value)
    plot_shap_distribution_by_cohort(
        shap_values, admission_labels, COHORT_PLOTS_DIR / "admission_vs_discharge_shap_distribution.png",
        "Total |SHAP| by Actual Admission Status",
    )
    logger.info("admission_vs_discharge: %s", {k: v["n"] for k, v in all_results["admission_vs_discharge"].items()})

    for cohort_name, source_variable in COHORT_DIMENSIONS:
        labels = reconstruct_categorical_from_onehot(validation_features, source_variable, encoder_metadata)
        all_results[cohort_name] = compare_cohorts(shap_values, feature_names, labels, expected_value)
        plot_shap_distribution_by_cohort(
            shap_values, labels, COHORT_PLOTS_DIR / f"{cohort_name}_shap_distribution.png",
            f"Total |SHAP| by {cohort_name.replace('_', ' ').title()}",
        )
        logger.info("%s: %s", cohort_name, {k: v["n"] for k, v in all_results[cohort_name].items()})

    (EXPLAINABILITY_REPORTS_DIR / "cohort_analysis.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    write_report(all_results)
    logger.info("Sprint 3 Milestone 6 (Cohort Analysis) completed successfully.")


def write_report(all_results: dict) -> None:
    lines = [
        "# Cohort Explainability Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Compares SHAP-based feature importance and mean predicted probability across patient "
        "subgroups. Cohort categories were reconstructed from their one-hot encoded columns "
        "using the encoder's own saved reference-category metadata, not hand-listed.",
        "",
    ]

    for cohort_name, groups in all_results.items():
        lines.append(f"## {cohort_name.replace('_', ' ').title()}")
        lines.append("")
        lines.append("| Group | N | Mean P(admit) | Top 5 Features by Mean \\|SHAP\\| |")
        lines.append("|---|---|---|---|")
        for group_name, group_data in groups.items():
            top_5 = ", ".join(list(group_data["top_features"].keys())[:5])
            lines.append(f"| {group_name} | {group_data['n']} | {group_data['mean_predicted_probability']:.4f} | {top_5} |")
        lines.append("")
        lines.append(f"Distribution plot: `cohort_plots/{cohort_name}_shap_distribution.png`")
        lines.append("")

    lines += [
        "## Interpretation",
        "",
        "Where the same 2-3 features top the ranking across every group within a dimension, "
        "the model is applying a consistent decision process rather than a different one per "
        "subgroup. Where the ranking or mean predicted probability differs substantially "
        "between groups, that reflects genuine differences in the underlying population risk "
        "(e.g. older-age cohorts having a higher base admission rate) rather than necessarily "
        "indicating a problem — see the age-group and admission-vs-discharge tables above, "
        "and the `AGE` dependence plot from Milestone 5 for the same signal from a different angle.",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "cohort_analysis_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
