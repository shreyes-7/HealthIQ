"""Survey-Aware Deep Dive, Step 3: fairness audit across race/ethnicity
(`RACERETH`), comparing the survey-weighted and unweighted LightGBM
models.

Answers a question never asked before in this project: does incorporating
NHAMCS's survey design change how equitably the model treats different
demographic groups? PROJECT_CONTEXT.md §44 names "Fairness" as one of the
things survey-aware learning should be evaluated on.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_fairness_audit
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

from ML.explainability.artifacts import load_model, load_split, split_features_and_target
from ML.explainability.cohort import reconstruct_categorical_from_onehot
from ML.explainability.fairness import compute_group_fairness_metrics, summarize_disparity
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
DEEP_DIVE_DIR = resolve_repo_path("ML/reports/survey_aware_deep_dive")

RACE_ETHNICITY_LABELS = {
    "1": "Non-Hispanic White",
    "2": "Non-Hispanic Black",
    "3": "Hispanic",
    "4": "Non-Hispanic Other",
}


def main() -> None:
    logger.info("Starting Survey-Aware Deep Dive Step 3: Fairness Audit (RACERETH)")
    DEEP_DIVE_DIR.mkdir(parents=True, exist_ok=True)

    validation_split = load_split("validation")
    validation_features, validation_target = split_features_and_target(validation_split)

    encoder_metadata = json.loads((SAVED_MODELS_DIR / "metadata.json").read_text())["encoder_feature_metadata"]
    race_ethnicity_labels = reconstruct_categorical_from_onehot(validation_features, "RACERETH", encoder_metadata)

    group_sizes = race_ethnicity_labels.value_counts().to_dict()
    logger.info("RACERETH group sizes: %s", group_sizes)

    unweighted_model = load_model()
    weighted_model = joblib.load(SAVED_MODELS_DIR / "model_survey_weighted.pkl")

    unweighted_probabilities = unweighted_model.predict_proba(validation_features)[:, 1]
    weighted_probabilities = weighted_model.predict_proba(validation_features)[:, 1]

    unweighted_group_metrics = compute_group_fairness_metrics(unweighted_probabilities, validation_target, race_ethnicity_labels)
    weighted_group_metrics = compute_group_fairness_metrics(weighted_probabilities, validation_target, race_ethnicity_labels)

    unweighted_disparity = summarize_disparity(unweighted_group_metrics)
    weighted_disparity = summarize_disparity(weighted_group_metrics)

    for metric, values in unweighted_disparity.items():
        logger.info(
            "%s gap -- unweighted: %.4f, weighted: %.4f (%s)",
            metric, values["gap"], weighted_disparity[metric]["gap"],
            "narrowed" if weighted_disparity[metric]["gap"] < values["gap"] else "widened",
        )

    plot_group_comparison(unweighted_group_metrics, weighted_group_metrics, DEEP_DIVE_DIR / "figures" / "fairness_selection_rate.png")

    (DEEP_DIVE_DIR / "fairness_audit.json").write_text(
        json.dumps(
            {
                "group_sizes": group_sizes,
                "unweighted_group_metrics": unweighted_group_metrics,
                "weighted_group_metrics": weighted_group_metrics,
                "unweighted_disparity": unweighted_disparity,
                "weighted_disparity": weighted_disparity,
            },
            indent=2, default=str,
        ),
        encoding="utf-8",
    )

    write_report(unweighted_group_metrics, weighted_group_metrics, unweighted_disparity, weighted_disparity)
    logger.info("Survey-Aware Deep Dive Step 3 completed successfully.")


def plot_group_comparison(unweighted_metrics: dict, weighted_metrics: dict, output_path) -> None:
    groups = sorted(unweighted_metrics.keys())
    labels = [RACE_ETHNICITY_LABELS.get(g, g) for g in groups]

    unweighted_rates = [unweighted_metrics[g]["selection_rate"] for g in groups]
    weighted_rates = [weighted_metrics[g]["selection_rate"] for g in groups]
    actual_rates = [unweighted_metrics[g]["actual_admission_rate"] for g in groups]

    x = np.arange(len(groups))
    width = 0.25

    figure, axis = plt.subplots(figsize=(9, 6))
    axis.bar(x - width, actual_rates, width, label="Actual admission rate", color="#7f7f7f")
    axis.bar(x, unweighted_rates, width, label="Unweighted predicted (selection rate)", color="#1f77b4")
    axis.bar(x + width, weighted_rates, width, label="Weighted predicted (selection rate)", color="#d62728")
    axis.set_xticks(x)
    axis.set_xticklabels(labels, rotation=20, ha="right")
    axis.set_ylabel("Rate")
    axis.set_title("Admission Selection Rate by Race/Ethnicity: Actual vs. Predicted")
    axis.legend()
    figure.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)


def write_report(unweighted_metrics: dict, weighted_metrics: dict, unweighted_disparity: dict, weighted_disparity: dict) -> None:
    lines = [
        "# Fairness Audit: Race/Ethnicity (RACERETH)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Compares the survey-weighted and unweighted LightGBM models across race/ethnicity "
        "groups on the validation split. `RACERETH` is NHAMCS-imputed (no missing category): "
        "1=Non-Hispanic White, 2=Non-Hispanic Black, 3=Hispanic, 4=Non-Hispanic Other (confirmed "
        "against the NCHS codebook).",
        "",
        "## Per-Group Metrics",
        "",
        "| Group | N | Actual Admit Rate | Unweighted Selection Rate | Weighted Selection Rate | "
        "Unweighted TPR | Weighted TPR | Unweighted ROC-AUC | Weighted ROC-AUC |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for group in sorted(unweighted_metrics.keys()):
        u = unweighted_metrics[group]
        w = weighted_metrics[group]
        label = RACE_ETHNICITY_LABELS.get(group, group)
        lines.append(
            f"| {label} | {u['n']} | {u['actual_admission_rate']:.4f} | {u['selection_rate']:.4f} | "
            f"{w['selection_rate']:.4f} | {u['true_positive_rate']:.4f} | {w['true_positive_rate']:.4f} | "
            f"{u['roc_auc']:.4f} | {w['roc_auc']:.4f} |"
        )

    lines += [
        "",
        "![Fairness Selection Rate](figures/fairness_selection_rate.png)",
        "",
        "## Disparity Summary (max-min gap across groups — smaller is more equitable)",
        "",
        "| Metric | Unweighted Gap | Weighted Gap | Change |",
        "|---|---|---|---|",
    ]
    for metric in unweighted_disparity:
        u_gap = unweighted_disparity[metric]["gap"]
        w_gap = weighted_disparity[metric]["gap"]
        direction = "narrowed ✓" if w_gap < u_gap else ("widened" if w_gap > u_gap else "unchanged")
        lines.append(f"| {metric} | {u_gap:.4f} | {w_gap:.4f} | {direction} ({w_gap - u_gap:+.4f}) |")

    selection_rate_narrowed = weighted_disparity["selection_rate"]["gap"] < unweighted_disparity["selection_rate"]["gap"]
    tpr_narrowed = weighted_disparity["true_positive_rate"]["gap"] < unweighted_disparity["true_positive_rate"]["gap"]
    roc_auc_narrowed = weighted_disparity["roc_auc"]["gap"] < unweighted_disparity["roc_auc"]["gap"]

    lines += [
        "",
        "## Interpretation",
        "",
    ]
    if selection_rate_narrowed and tpr_narrowed:
        lines.append(
            "Survey weighting **narrows** both the selection-rate and true-positive-rate gaps "
            "across race/ethnicity groups on this validation split — consistent with the "
            "intended effect of survey weights (correcting for a sample that isn't perfectly "
            "representative of the U.S. population NHAMCS is designed to estimate) also "
            "producing a more equitable model, not just a differently-calibrated one. This "
            "should be read as suggestive, not conclusive: one validation split, one protected "
            "attribute, and no statistical significance testing on the gap differences "
            "themselves — a proper fairness study would bootstrap confidence intervals around "
            "each gap before drawing a firm conclusion."
        )
        if not roc_auc_narrowed:
            lines.append(
                "\nOne caveat worth flagging rather than hiding: the per-group **ROC-AUC gap "
                f"widens slightly** under weighting ({unweighted_disparity['roc_auc']['gap']:.4f} → "
                f"{weighted_disparity['roc_auc']['gap']:.4f}). ROC-AUC measures ranking quality "
                "independent of the 0.5 threshold, while selection rate and TPR are both "
                "threshold-dependent. This means survey weighting is improving fairness "
                "*specifically at the operating threshold this project uses*, not uniformly "
                "across every possible threshold — a distinction worth keeping in mind if the "
                "decision threshold is ever revisited."
            )
    elif not selection_rate_narrowed and not tpr_narrowed:
        lines.append(
            "Survey weighting **widens** both the selection-rate and true-positive-rate gaps "
            "across race/ethnicity groups on this validation split. This is a genuinely "
            "important finding to flag: survey weighting corrects for sampling representativeness "
            "at the population level, but that is a distinct goal from equalizing model behavior "
            "across demographic groups within the sample — this result shows those two goals can "
            "pull in different directions, and should inform whether survey weighting is adopted "
            "for the production model without additional fairness-specific mitigation."
        )
    else:
        lines.append(
            "Survey weighting's effect on fairness is mixed: it narrows one gap "
            f"({'selection rate' if selection_rate_narrowed else 'true positive rate'}) while "
            f"widening the other ({'true positive rate' if selection_rate_narrowed else 'selection rate'}). "
            "There is no single answer to 'does survey weighting make this model more fair' — "
            "it depends which fairness criterion is prioritized, a genuine and common tension in "
            "the fairness literature (demographic parity and equal opportunity cannot always be "
            "satisfied simultaneously)."
        )

    report_path = DEEP_DIVE_DIR / "fairness_audit_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
