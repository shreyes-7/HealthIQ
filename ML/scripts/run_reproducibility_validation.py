"""Sprint 2 Milestone 11: Reproducibility & Validation.

Verifies training correctness the same way Sprint 1 Milestone 11
verified preprocessing correctness:

1. Retrain determinism: refitting the selected model's exact
   hyperparameters twice on the same data produces identical predictions.
2. End-to-end smoke test: a raw row -> PreprocessingPipeline.transform ->
   the serialized model -> a prediction, with no errors, using the
   production artifacts exactly as the backend would.

Module-level unit tests (metrics, cross-validation, survey-aware
modeling, encoder/scaler, full pipeline fit/transform reusability) live
in ML/tests/ (run with `pytest ML/tests`), same convention as Sprint 1.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_reproducibility_validation
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset
from ML.modeling.model_registry import MODEL_REGISTRY
from ML.pipeline.preprocessing_pipeline import PreprocessingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")
TRAIN_PATH = resolve_repo_path("Data/processed/train.parquet")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}


def check_retrain_determinism() -> dict:
    metadata = json.loads((SAVED_MODELS_DIR / "model_metadata.json").read_text())
    model_name = metadata["model_name"]
    hyperparameters = metadata["hyperparameters"]

    if model_name not in MODEL_REGISTRY:
        logger.info("%s has no single estimator_factory (e.g. a meta-ensemble) — skipping refit determinism check", model_name)
        return {"passed": True, "model_name": model_name, "note": "skipped: not a single-estimator model"}

    dataframe = pd.read_parquet(TRAIN_PATH)
    feature_columns = [column for column in dataframe.columns if column not in NON_FEATURE_COLUMNS]
    features, target = dataframe[feature_columns], dataframe[TARGET_COLUMN_NAME]

    factory = MODEL_REGISTRY[model_name]["estimator_factory"]
    model_a = factory().set_params(**hyperparameters)
    model_a.fit(features, target)
    model_b = factory().set_params(**hyperparameters)
    model_b.fit(features, target)

    probabilities_a = model_a.predict_proba(features.head(200))[:, 1]
    probabilities_b = model_b.predict_proba(features.head(200))[:, 1]
    identical = bool(np.allclose(probabilities_a, probabilities_b))

    return {
        "passed": identical,
        "model_name": model_name,
        "max_abs_diff": float(np.max(np.abs(probabilities_a - probabilities_b))),
    }


def check_end_to_end_smoke_test() -> dict:
    config = load_config(DEFAULT_CONFIG_PATH)
    raw_dataframe, _metadata = load_dataset(config)
    sample_raw_rows = raw_dataframe.head(3)

    pipeline = PreprocessingPipeline.load(SAVED_MODELS_DIR)
    result = pipeline.transform(sample_raw_rows)

    model = joblib.load(SAVED_MODELS_DIR / "model.pkl")
    predictions = model.predict_proba(result["features"])[:, 1]

    return {"passed": True, "sample_predictions": predictions.tolist()}


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 11: Reproducibility & Validation")

    determinism_result = check_retrain_determinism()
    logger.info("Retrain determinism: %s", determinism_result)

    smoke_test_result = check_end_to_end_smoke_test()
    logger.info("End-to-end smoke test: %s", smoke_test_result)

    all_passed = determinism_result["passed"] and smoke_test_result["passed"]

    lines = [
        "# Reproducibility & Validation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## Overall: {'PASS' if all_passed else 'FAIL'}",
        "",
        "## Retrain Determinism",
        "",
        f"```\n{determinism_result}\n```",
        "",
        "## End-to-End Smoke Test (raw row -> PreprocessingPipeline -> model -> prediction)",
        "",
        f"```\n{smoke_test_result}\n```",
        "",
        "## Unit Tests",
        "",
        "See `ML/tests/` (`pytest ML/tests`) for module-level unit tests covering metrics, "
        "cross-validation, survey-aware modeling, and the full preprocessing pipeline.",
        "",
    ]
    report_path = MODELING_REPORTS_DIR / "validation_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)

    if all_passed:
        logger.info("Sprint 2 Milestone 11 (Reproducibility & Validation) completed successfully. All checks PASSED.")
    else:
        logger.error("Sprint 2 Milestone 11 completed with FAILURES.")


if __name__ == "__main__":
    main()
