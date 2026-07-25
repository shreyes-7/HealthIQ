"""Sprint 2 Milestone 9: Final Model Selection.

Applies predefined selection criteria to the model comparison table
(PROJECT_CONTEXT.md Section 39: "automatically identify the best-
performing model based on predefined evaluation criteria") and evaluates
the selected model on the test split -- exactly once, since the test
split must stay untouched until this final confirmation step.

Selection criteria (in order):
1. Primary metric: PR-AUC on the validation split. Chosen over ROC-AUC
   for the final pick (though ROC-AUC drove hyperparameter search) because
   PR-AUC is more informative than ROC-AUC under the ~13% positive rate --
   it is far more sensitive to how well the model ranks the minority
   (admitted) class, which is the clinically important one.
2. Tie-breaker: recall/sensitivity, since under-predicting admission risk
   is the costlier clinical error for a decision-support tool.
3. Tie-breaker: training + inference time (lower is better) and
   interpretability, as explicit secondary considerations from
   PROJECT_CONTEXT.md Section 40.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_final_model_selection
"""

import logging
from datetime import datetime, timezone

import joblib
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path
from ML.modeling.metrics import compute_classification_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TEST_PATH = resolve_repo_path("Data/processed/test.parquet")
CANDIDATE_MODELS_DIR = resolve_repo_path("ML/saved_models/candidates")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}


def select_best_model(comparison_table: pd.DataFrame) -> pd.Series:
    ranked = comparison_table.sort_values(
        by=["pr_auc", "recall", "training_time_seconds"], ascending=[False, False, True]
    )
    return ranked.iloc[0]


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 9: Final Model Selection")

    comparison_table = pd.read_csv(MODELING_REPORTS_DIR / "model_comparison.csv")
    best_row = select_best_model(comparison_table)
    best_model_name = best_row["model"]
    logger.info("Selected model: %s (validation PR-AUC %.4f, ROC-AUC %.4f)", best_model_name, best_row["pr_auc"], best_row["roc_auc"])

    best_model = joblib.load(CANDIDATE_MODELS_DIR / f"{best_model_name}.pkl")

    test_dataframe = pd.read_parquet(TEST_PATH)
    feature_columns = [column for column in test_dataframe.columns if column not in NON_FEATURE_COLUMNS]
    features_test, target_test = test_dataframe[feature_columns], test_dataframe[TARGET_COLUMN_NAME]

    test_probabilities = best_model.predict_proba(features_test)[:, 1]
    test_metrics = compute_classification_metrics(target_test, test_probabilities)
    logger.info(
        "%s on TEST split: ROC-AUC %.4f, PR-AUC %.4f, F1 %.4f, recall %.4f",
        best_model_name, test_metrics["roc_auc"], test_metrics["pr_auc"], test_metrics["f1"], test_metrics["recall"],
    )

    lines = [
        "# Final Model Selection Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Selection Criteria",
        "",
        "1. Primary: validation PR-AUC (more informative than ROC-AUC at ~13% positive rate)",
        "2. Tie-breaker: recall/sensitivity (under-predicting admission risk is the costlier clinical error)",
        "3. Tie-breaker: training time, then interpretability",
        "",
        f"## Selected Model: `{best_model_name}`",
        "",
        "### Validation metrics (informed the selection)",
        "",
        pd.DataFrame([best_row]).round(4).to_markdown(index=False),
        "",
        "### Test split metrics (confirmation only -- evaluated exactly once)",
        "",
        pd.DataFrame([test_metrics]).drop(columns=["confusion_matrix"]).round(4).to_markdown(index=False),
        "",
        f"Confusion matrix (test): {test_metrics['confusion_matrix']}",
        "",
    ]

    report_path = MODELING_REPORTS_DIR / "final_model_selection.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)

    logger.info("Sprint 2 Milestone 9 (Final Model Selection) completed successfully.")


if __name__ == "__main__":
    main()
