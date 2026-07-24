"""Sprint 2 Milestone 8: Survey-Aware Model comparison.

Compares the conventional (unweighted) Logistic Regression baseline
against a survey-weighted version (sample_weight=PATWT), then runs a
focused GLM inference comparison (weighted vs. weighted+cluster-robust)
on a small, interpretable feature subset to see whether accounting for
the clustered sample design (CPSUM) changes which predictors appear
statistically significant.

Explicitly a first pass -- see ML/modeling/survey_aware.py docstring for
what this does and does not cover relative to PROJECT_CONTEXT.md Section 44's
full research objective. No model trained here is treated as the Sprint 2
"selected" model; this is a research comparison, not a candidate for
Milestone 9's selection.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_survey_aware_comparison
"""

import logging
from datetime import datetime, timezone

import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path
from ML.modeling.survey_aware import (
    compare_weighted_vs_unweighted,
    fit_survey_glm,
    select_focused_features,
    summarize_glm_significance,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TRAIN_PATH = resolve_repo_path("Data/processed/train.parquet")
VALIDATION_PATH = resolve_repo_path("Data/processed/validation.parquet")
FEATURE_IMPORTANCE_PATH = resolve_repo_path("ML/reports/feature_engineering/feature_importance_scores.csv")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}


def load_split(path):
    dataframe = pd.read_parquet(path)
    feature_columns = [column for column in dataframe.columns if column not in NON_FEATURE_COLUMNS]
    return dataframe, feature_columns


def write_report(predictive_comparison: dict, glm_comparison: pd.DataFrame, focused_features: list[str]) -> None:
    unweighted = predictive_comparison["unweighted_validation_metrics"]
    weighted = predictive_comparison["weighted_validation_metrics"]

    significant_unweighted = set(glm_comparison[glm_comparison["significant_unweighted"]].index)
    significant_cluster_robust = set(glm_comparison[glm_comparison["significant_cluster_robust"]].index)
    only_unweighted = significant_unweighted - significant_cluster_robust
    only_cluster_robust = significant_cluster_robust - significant_unweighted

    lines = [
        "# Survey-Aware Model Comparison Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "**Scope**: a first pass, not the full research program PROJECT_CONTEXT.md Section 44 "
        "envisions. Two comparisons are made — see `ML/modeling/survey_aware.py` docstring for "
        "the reasoning behind each.",
        "",
        "## 1. Predictive Comparison (full 866-feature set)",
        "",
        "Same `LogisticRegression`, same features, same validation split — only difference is "
        "`sample_weight=PATWT` on the weighted version.",
        "",
        "| Metric | Unweighted (conventional) | Weighted (survey-aware) |",
        "|---|---|---|",
    ]
    for metric_name in ("accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc", "brier_score"):
        lines.append(f"| {metric_name} | {unweighted[metric_name]:.4f} | {weighted[metric_name]:.4f} |")

    lines += [
        "",
        "## 2. Inference Comparison (focused feature subset)",
        "",
        f"Features used ({len(focused_features)}, Sprint 1's top-ranked by combined importance): "
        f"{focused_features}",
        "",
        "Weighted GLM (survey weight only, `var_weights=PATWT`) vs. the same GLM with "
        "cluster-robust standard errors (clustering on `CPSUM`, the PSU variable) — isolates what "
        "accounting for the clustered sample design changes, beyond weighting alone.",
        "",
        "**Known limitation**: statsmodels emits `SpecificationWarning: cov_type not fully "
        "supported with var_weights` for the cluster-robust fit (a genuine statsmodels "
        "constraint, present regardless of weight type). The cluster-robust standard errors below "
        "should be read as exploratory, not textbook-rigorous design-based inference — a dedicated "
        "survey-design library would be needed for that, out of scope for this first pass.",
        "",
        glm_comparison.round(4).to_markdown(),
        "",
        f"- Significant (p < 0.05) under weighting alone but NOT after cluster correction: {sorted(only_unweighted) or 'none'}",
        f"- Significant only after cluster correction: {sorted(only_cluster_robust) or 'none'}",
        "",
        "If either list above is non-empty, it means the naive (non-cluster-robust) model would "
        "have over- or under-stated confidence in that predictor — exactly the kind of finding "
        "PROJECT_CONTEXT.md's survey-aware research objective is asking about.",
        "",
    ]

    report_path = MODELING_REPORTS_DIR / "survey_aware_comparison.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 8: Survey-Aware Model Comparison")
    MODELING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    train_df, feature_columns = load_split(TRAIN_PATH)
    val_df, _ = load_split(VALIDATION_PATH)

    features_train, target_train, weights_train = train_df[feature_columns], train_df[TARGET_COLUMN_NAME], train_df["PATWT"]
    features_val, target_val = val_df[feature_columns], val_df[TARGET_COLUMN_NAME]

    logger.info("Comparing unweighted vs. survey-weighted Logistic Regression (full feature set)")
    predictive_comparison = compare_weighted_vs_unweighted(
        features_train, target_train, weights_train, features_val, target_val
    )
    logger.info(
        "Unweighted ROC-AUC %.4f vs weighted ROC-AUC %.4f",
        predictive_comparison["unweighted_validation_metrics"]["roc_auc"],
        predictive_comparison["weighted_validation_metrics"]["roc_auc"],
    )

    focused_features = select_focused_features(FEATURE_IMPORTANCE_PATH, feature_columns)
    logger.info("Focused GLM feature subset: %s", focused_features)

    weighted_glm = fit_survey_glm(features_train[focused_features], target_train, weights_train)
    cluster_robust_glm = fit_survey_glm(
        features_train[focused_features], target_train, weights_train, clusters=train_df["CPSUM"]
    )

    weighted_summary = summarize_glm_significance(weighted_glm)
    cluster_robust_summary = summarize_glm_significance(cluster_robust_glm)

    comparison = pd.DataFrame(
        {
            "coefficient": weighted_summary["coefficient"],
            "weighted_std_error": weighted_summary["std_error"],
            "weighted_p_value": weighted_summary["p_value"],
            "significant_unweighted": weighted_summary["significant_at_0.05"],
            "cluster_robust_std_error": cluster_robust_summary["std_error"],
            "cluster_robust_p_value": cluster_robust_summary["p_value"],
            "significant_cluster_robust": cluster_robust_summary["significant_at_0.05"],
        }
    )
    comparison.to_csv(MODELING_REPORTS_DIR / "survey_aware_glm_comparison.csv")
    logger.info("Wrote survey_aware_glm_comparison.csv")

    write_report(predictive_comparison, comparison, focused_features)

    logger.info("Sprint 2 Milestone 8 (Survey-Aware Model) completed successfully.")


if __name__ == "__main__":
    main()
