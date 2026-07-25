"""Survey-Aware Deep Dive, Step 1: fit a survey-weighted LightGBM and
compare it against the production (unweighted) LightGBM on both the
validation and test splits.

This is the piece Sprint 2 Milestone 8 was missing: the actual production
model, evaluated in a survey-aware form, not just Logistic Regression.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_survey_aware_lightgbm
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd

from ML.explainability.artifacts import load_model, split_features_and_target
from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path
from ML.modeling.metrics import compute_classification_metrics
from ML.modeling.survey_aware_lightgbm import fit_survey_weighted_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = resolve_repo_path("Data/processed")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
DEEP_DIVE_DIR = resolve_repo_path("ML/reports/survey_aware_deep_dive")


def load_split_with_weight(name: str):
    frame = pd.read_parquet(PROCESSED_DATA_DIR / f"{name}.parquet")
    features, target = split_features_and_target(frame)
    return features, target, frame["PATWT"]


def main() -> None:
    logger.info("Starting Survey-Aware Deep Dive Step 1: Weighted vs. Unweighted LightGBM")
    DEEP_DIVE_DIR.mkdir(parents=True, exist_ok=True)

    train_features, train_target, train_weights = load_split_with_weight("train")
    validation_features, validation_target, _validation_weights = load_split_with_weight("validation")
    test_features, test_target, _test_weights = load_split_with_weight("test")

    logger.info("Fitting survey-weighted LightGBM (sample_weight=PATWT, production hyperparameters)")
    weighted_model = fit_survey_weighted_model(train_features, train_target, train_weights)

    unweighted_model = load_model()  # the exact production model, not refit

    results = {}
    for split_name, features, target in (
        ("validation", validation_features, validation_target),
        ("test", test_features, test_target),
    ):
        weighted_proba = weighted_model.predict_proba(features)[:, 1]
        unweighted_proba = unweighted_model.predict_proba(features)[:, 1]

        results[split_name] = {
            "weighted": compute_classification_metrics(target, weighted_proba),
            "unweighted": compute_classification_metrics(target, unweighted_proba),
        }
        logger.info(
            "%s split -- unweighted ROC-AUC %.4f, PR-AUC %.4f | weighted ROC-AUC %.4f, PR-AUC %.4f",
            split_name,
            results[split_name]["unweighted"]["roc_auc"], results[split_name]["unweighted"]["pr_auc"],
            results[split_name]["weighted"]["roc_auc"], results[split_name]["weighted"]["pr_auc"],
        )

    weighted_model_path = SAVED_MODELS_DIR / "model_survey_weighted.pkl"
    joblib.dump(weighted_model, weighted_model_path)
    logger.info("Saved %s", weighted_model_path)

    (DEEP_DIVE_DIR / "weighted_vs_unweighted_metrics.json").write_text(
        json.dumps(results, indent=2, default=str), encoding="utf-8"
    )

    write_report(results)
    logger.info("Survey-Aware Deep Dive Step 1 completed successfully.")


def write_report(results: dict) -> None:
    lines = [
        "# Survey-Weighted vs. Unweighted LightGBM",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Same LightGBM hyperparameters (from `experiment_log.json`, the exact production "
        "tuning result), same training data, same `class_weight=\"balanced\"` setting -- the "
        "**only** difference is `sample_weight=PATWT` on the weighted variant. This isolates "
        "the effect of survey weighting specifically, the same experimental design Sprint 2 "
        "used for its Logistic Regression comparison, now applied to the actual production "
        "model for the first time.",
        "",
    ]

    for split_name, split_results in results.items():
        lines.append(f"## {split_name.title()} Split")
        lines.append("")
        lines.append("| Metric | Unweighted (production) | Weighted (survey-aware) | Difference |")
        lines.append("|---|---|---|---|")
        for metric in ("accuracy", "precision", "recall", "specificity", "f1", "roc_auc", "pr_auc", "brier_score"):
            unweighted_value = split_results["unweighted"][metric]
            weighted_value = split_results["weighted"][metric]
            lines.append(f"| {metric} | {unweighted_value:.4f} | {weighted_value:.4f} | {weighted_value - unweighted_value:+.4f} |")
        lines.append("")

    lines += [
        "## Interpretation",
        "",
        "As in Sprint 2's Logistic Regression comparison, expect the weighted model's raw "
        "discrimination metrics on this sample to be lower, not higher -- `PATWT` up-weights "
        "visits from underrepresented sampling strata to better reflect the U.S. population "
        "NHAMCS samples, which trades some in-sample predictive accuracy for population "
        "representativeness. That is the expected, correct behavior of a survey-weighted "
        "estimator, not a sign the weighted model is worse in an absolute sense -- see the "
        "fairness audit (`fairness_audit_report.md`) for whether that trade produces a more "
        "equitable model across demographic groups, which is the more relevant question for "
        "this project's research objective than raw accuracy alone.",
    ]

    report_path = DEEP_DIVE_DIR / "weighted_vs_unweighted_lightgbm.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
