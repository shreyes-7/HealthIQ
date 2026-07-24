"""Sprint 2 Milestone 10: Model Serialization & Versioning.

Persists the model selected in Milestone 9 as ML/saved_models/model.pkl
plus a metadata sidecar (version, training date, hyperparameters,
metrics, feature list) consumable by the backend without retraining
(PROJECT_CONTEXT.md Sections 46/48). Confirms it loads and predicts
correctly using Sprint 1's PreprocessingPipeline output directly.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_model_serialization
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path
from ML.modeling.experiment_log import ExperimentLog

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CANDIDATE_MODELS_DIR = resolve_repo_path("ML/saved_models/candidates")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")
FEATURE_NAMES_PATH = resolve_repo_path("ML/saved_models/feature_names.json")
VALIDATION_PATH = resolve_repo_path("Data/processed/validation.parquet")

MODEL_VERSION = "1.0.0"


def select_best_model_name(comparison_table: pd.DataFrame) -> str:
    """Mirrors Milestone 9's selection criteria exactly, so serialization
    always matches whatever run_final_model_selection.py chose."""
    ranked = comparison_table.sort_values(
        by=["pr_auc", "recall", "training_time_seconds"], ascending=[False, False, True]
    )
    return ranked.iloc[0]["model"]


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 10: Model Serialization & Versioning")

    comparison_table = pd.read_csv(MODELING_REPORTS_DIR / "model_comparison.csv")
    best_model_name = select_best_model_name(comparison_table)
    logger.info("Selected model for serialization: %s", best_model_name)

    model = joblib.load(CANDIDATE_MODELS_DIR / f"{best_model_name}.pkl")
    experiment_log = ExperimentLog.load(MODELING_REPORTS_DIR / "experiment_log.json")
    record = experiment_log.get(best_model_name)
    feature_names = json.loads(FEATURE_NAMES_PATH.read_text())

    model_path = SAVED_MODELS_DIR / "model.pkl"
    joblib.dump(model, model_path)
    logger.info("Wrote %s", model_path)

    metadata = {
        "model_name": best_model_name,
        "version": MODEL_VERSION,
        "trained_at": record.trained_at,
        "serialized_at": datetime.now(timezone.utc).isoformat(),
        "hyperparameters": record.hyperparameters,
        "cross_validation": record.cross_validation["aggregated"],
        "validation_metrics": record.validation_metrics,
        "feature_count": len(feature_names),
        "target_column": TARGET_COLUMN_NAME,
        "training_data": "Data/processed/train.parquet (Sprint 1 PreprocessingPipeline, fit on training split only)",
        "preprocessing_pipeline": "ML/saved_models/preprocessing_pipeline.pkl",
    }
    metadata_path = SAVED_MODELS_DIR / "model_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote %s", metadata_path)

    reloaded_model = joblib.load(model_path)
    sample = pd.read_parquet(VALIDATION_PATH).head(5)
    feature_columns = [column for column in sample.columns if column in feature_names]
    predictions = reloaded_model.predict_proba(sample[feature_columns])[:, 1]
    logger.info("Reload + predict smoke test OK: sample probabilities %s", predictions.tolist())

    logger.info("Sprint 2 Milestone 10 (Model Serialization & Versioning) completed successfully.")


if __name__ == "__main__":
    main()
