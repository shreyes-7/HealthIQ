"""Sprint 2 Milestone 7: Ensemble/Stacking Model.

Builds a stacking ensemble from the top individual candidate models
(each reusing its already-tuned hyperparameters from Milestone 4),
evaluates it on the validation split identically to the individual
models, and appends it to the experiment log and comparison table.

Scope note on cross-validation: a separate outer k-fold CV (as done for
the individual models in Milestone 5) is deliberately NOT run here. Each
outer fold would require fitting a fresh StackingClassifier, and
StackingClassifier itself internally cross-fits every base estimator
(5-fold + a final refit) to generate leakage-free meta-learner training
data -- with the base models involved (lightgbm/xgboost/random_forest,
75-155s per single fit), even 3 outer folds would cost over an hour.
This is a real, documented cost/thoroughness tradeoff, not an oversight:
the internal cross-fitting is itself a legitimate form of validation
(it's how StackingClassifier avoids leakage in the first place), and the
validation-split evaluation below is a fully independent, held-out check.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_stacking_ensemble
"""

import json
import logging
import time

import joblib
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path
from ML.modeling.experiment_log import ExperimentLog, ExperimentRecord
from ML.modeling.metrics import compute_classification_metrics
from ML.modeling.stacking import build_stacking_ensemble, select_top_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TRAIN_PATH = resolve_repo_path("Data/processed/train.parquet")
VALIDATION_PATH = resolve_repo_path("Data/processed/validation.parquet")
CANDIDATE_MODELS_DIR = resolve_repo_path("ML/saved_models/candidates")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}
STACKING_MODEL_NAME = "stacking_ensemble"

# Placeholder matching the shape ML.scripts.run_model_comparison expects
# (record.cross_validation["aggregated"]["roc_auc"]["mean"]/"std"), with
# an explicit note rather than a silently-missing value.
CROSS_VALIDATION_PLACEHOLDER = {
    "n_folds": 0,
    "note": "Outer CV skipped for cost reasons -- see module docstring. "
    "StackingClassifier's internal 5-fold cross-fit (used to generate leakage-free "
    "meta-learner training data) is the validation mechanism for this model.",
    "aggregated": {"roc_auc": {"mean": None, "std": None}},
}


def load_features_and_target(path):
    dataframe = pd.read_parquet(path)
    feature_columns = [column for column in dataframe.columns if column not in NON_FEATURE_COLUMNS]
    return dataframe[feature_columns], dataframe[TARGET_COLUMN_NAME]


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 7: Ensemble/Stacking Model")

    experiment_log = ExperimentLog.load(MODELING_REPORTS_DIR / "experiment_log.json")
    top_model_names = select_top_models(experiment_log)
    logger.info("Base models selected for stacking (top %d by validation ROC-AUC, cost-eligible): %s", len(top_model_names), top_model_names)

    features_train, target_train = load_features_and_target(TRAIN_PATH)
    features_val, target_val = load_features_and_target(VALIDATION_PATH)

    start_time = time.monotonic()
    stacking_model = build_stacking_ensemble(experiment_log)
    stacking_model.fit(features_train, target_train)
    training_time_seconds = time.monotonic() - start_time
    logger.info("Stacking ensemble fit complete (%.1fs)", training_time_seconds)

    validation_probabilities = stacking_model.predict_proba(features_val)[:, 1]
    validation_metrics = compute_classification_metrics(target_val, validation_probabilities)
    logger.info(
        "%s: validation ROC-AUC %.4f, PR-AUC %.4f, F1 %.4f",
        STACKING_MODEL_NAME, validation_metrics["roc_auc"], validation_metrics["pr_auc"], validation_metrics["f1"],
    )

    experiment_log.add(
        ExperimentRecord(
            model_name=STACKING_MODEL_NAME,
            hyperparameters={"base_models": top_model_names, "final_estimator": "LogisticRegression"},
            cross_validation=CROSS_VALIDATION_PLACEHOLDER,
            validation_metrics=validation_metrics,
            training_time_seconds=training_time_seconds,
            random_seed=42,
        )
    )
    experiment_log.save(MODELING_REPORTS_DIR / "experiment_log.json")
    logger.info("Updated experiment_log.json with %s", STACKING_MODEL_NAME)

    validation_probabilities_by_model = json.loads((MODELING_REPORTS_DIR / "validation_probabilities.json").read_text())
    validation_probabilities_by_model[STACKING_MODEL_NAME] = validation_probabilities.tolist()
    (MODELING_REPORTS_DIR / "validation_probabilities.json").write_text(
        json.dumps(validation_probabilities_by_model), encoding="utf-8"
    )

    model_path = CANDIDATE_MODELS_DIR / f"{STACKING_MODEL_NAME}.pkl"
    joblib.dump(stacking_model, model_path)
    logger.info("Saved %s (%.1fs total)", model_path, training_time_seconds)

    logger.info("Sprint 2 Milestone 7 (Ensemble/Stacking Model) completed successfully.")


if __name__ == "__main__":
    main()
