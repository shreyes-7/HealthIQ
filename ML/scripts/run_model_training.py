"""Sprint 2 Milestones 2-5: Baseline models, ensemble/boosting models,
hyperparameter tuning, and cross-validated evaluation for every candidate
model in ML.modeling.model_registry.

For each model: hyperparameter search on the training split -> 5-fold
cross-validation with the best params -> fit on the full training split
-> evaluate on the validation split -> log the experiment -> save the
fitted candidate model.

Reuses Sprint 1's PreprocessingPipeline output directly
(Data/processed/{train,validation}.parquet) -- no data is re-preprocessed
here, and the raw dataset is never touched.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_model_training
"""

import json
import logging
import time
import warnings

import joblib
import pandas as pd

# This sklearn version deprecated the `penalty` param in favor of `l1_ratio`
# but still honors `penalty` correctly (verified: L1 vs L2 selection differs
# as expected in tuning results) -- silenced here since it fires on every
# one of hundreds of fits and would otherwise dominate the log.
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.linear_model._logistic")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.linear_model._logistic")

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path
from ML.modeling.cross_validation import cross_validate_model
from ML.modeling.experiment_log import ExperimentLog, ExperimentRecord
from ML.modeling.metrics import compute_classification_metrics
from ML.modeling.model_registry import MODEL_REGISTRY
from ML.modeling.tuning import tune_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TRAIN_PATH = resolve_repo_path("Data/processed/train.parquet")
VALIDATION_PATH = resolve_repo_path("Data/processed/validation.parquet")
CANDIDATE_MODELS_DIR = resolve_repo_path("ML/saved_models/candidates")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}


def load_features_and_target(path):
    dataframe = pd.read_parquet(path)
    feature_columns = [column for column in dataframe.columns if column not in NON_FEATURE_COLUMNS]
    return dataframe[feature_columns], dataframe[TARGET_COLUMN_NAME]


def train_and_evaluate_one_model(model_name, spec, features_train, target_train, features_val, target_val, experiment_log):
    logger.info("=== %s: starting ===", model_name)
    start_time = time.monotonic()

    tuning_result = tune_model(spec["estimator_factory"](), spec["param_distributions"], features_train, target_train)
    best_model = tuning_result["best_estimator"]
    logger.info(
        "%s: best params %s (search ROC-AUC %.4f)",
        model_name, tuning_result["best_params"], tuning_result["best_search_score"],
    )

    untrained_best = spec["estimator_factory"]().set_params(**tuning_result["best_params"])
    cv_result = cross_validate_model(untrained_best, features_train, target_train)
    logger.info(
        "%s: 5-fold CV ROC-AUC %.4f +/- %.4f",
        model_name, cv_result["aggregated"]["roc_auc"]["mean"], cv_result["aggregated"]["roc_auc"]["std"],
    )

    # best_model was already refit on the full training split by RandomizedSearchCV (refit=True).
    validation_probabilities = best_model.predict_proba(features_val)[:, 1]
    validation_metrics = compute_classification_metrics(target_val, validation_probabilities)
    logger.info(
        "%s: validation ROC-AUC %.4f, PR-AUC %.4f, F1 %.4f",
        model_name, validation_metrics["roc_auc"], validation_metrics["pr_auc"], validation_metrics["f1"],
    )

    training_time_seconds = time.monotonic() - start_time

    experiment_log.add(
        ExperimentRecord(
            model_name=model_name,
            hyperparameters=tuning_result["best_params"],
            cross_validation=cv_result,
            validation_metrics=validation_metrics,
            training_time_seconds=training_time_seconds,
            random_seed=42,
        )
    )

    model_path = CANDIDATE_MODELS_DIR / f"{model_name}.pkl"
    joblib.dump(best_model, model_path)
    logger.info("%s: saved to %s (%.1fs total)", model_name, model_path, training_time_seconds)

    return validation_probabilities


def main() -> None:
    logger.info("Starting Sprint 2 Milestones 2-5: training, tuning, cross-validation, evaluation")
    CANDIDATE_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    MODELING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    features_train, target_train = load_features_and_target(TRAIN_PATH)
    features_val, target_val = load_features_and_target(VALIDATION_PATH)
    logger.info("Train %s, Validation %s", features_train.shape, features_val.shape)

    experiment_log = ExperimentLog()
    validation_probabilities_by_model = {}

    for model_name, spec in MODEL_REGISTRY.items():
        validation_probabilities = train_and_evaluate_one_model(
            model_name, spec, features_train, target_train, features_val, target_val, experiment_log
        )
        validation_probabilities_by_model[model_name] = validation_probabilities.tolist()

    experiment_log.save(MODELING_REPORTS_DIR / "experiment_log.json")
    logger.info("Wrote experiment_log.json (%d models)", len(experiment_log.records))

    (MODELING_REPORTS_DIR / "validation_probabilities.json").write_text(
        json.dumps(validation_probabilities_by_model), encoding="utf-8"
    )
    (MODELING_REPORTS_DIR / "validation_targets.json").write_text(
        json.dumps(target_val.tolist()), encoding="utf-8"
    )

    logger.info("Sprint 2 Milestones 2-5 completed successfully.")


if __name__ == "__main__":
    main()
