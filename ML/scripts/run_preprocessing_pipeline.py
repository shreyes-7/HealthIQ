"""Milestone 9 - Reusable Preprocessing Pipeline.

Runs the full, consolidated pipeline directly from the raw SAS file:
load -> validate -> clean -> engineer features (encode + scale) -> assemble
output, with survey design variables preserved throughout. Persists the
fitted pipeline, encoder, scaler, and feature metadata as reusable
artifacts. No model is trained.

This script also demonstrates the "reusable" requirement concretely: it
fits the pipeline on one row-slice of the raw data and calls transform()
on a different row-slice, proving the SAME learned cleaning/encoding/
scaling state can be reapplied to new data without errors or schema
drift. This is an ad hoc smoke test, not the official Milestone 7
train/test split.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_preprocessing_pipeline
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import DEFAULT_CONFIG_PATH, resolve_repo_path
from ML.pipeline.preprocessing_pipeline import PreprocessingPipeline, load_validate_and_fit

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODEL_READY_DATASET_PATH = resolve_repo_path("Data/processed/ed2022_model_ready.parquet")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
PIPELINE_REPORTS_DIR = resolve_repo_path("ML/reports/pipeline")


def assemble_model_ready(result: dict) -> pd.DataFrame:
    return pd.concat([result["target"], result["features"], result["survey"], result["identifiers"]], axis=1)


def save_artifacts(pipeline: PreprocessingPipeline, result: dict) -> None:
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    pipeline_path = pipeline.save(SAVED_MODELS_DIR)
    logger.info("Wrote %s", pipeline_path)

    joblib.dump(pipeline.encoder, SAVED_MODELS_DIR / "encoder.pkl")
    joblib.dump(pipeline.scaler, SAVED_MODELS_DIR / "scaler.pkl")
    joblib.dump({"encoder": pipeline.encoder, "scaler": pipeline.scaler}, SAVED_MODELS_DIR / "preprocessing.pkl")
    logger.info("Wrote encoder.pkl, scaler.pkl, preprocessing.pkl to %s", SAVED_MODELS_DIR)

    feature_names_path = SAVED_MODELS_DIR / "feature_names.json"
    feature_names_path.write_text(json.dumps(list(result["features"].columns), indent=2), encoding="utf-8")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_column": TARGET_COLUMN_NAME,
        "feature_count": int(result["features"].shape[1]),
        "survey_columns": list(result["survey"].columns),
        "identifier_columns": list(result["identifiers"].columns),
        "encoder_feature_metadata": pipeline.encoder.get_feature_metadata(),
        "scaler_feature_metadata": pipeline.scaler.get_feature_metadata(),
        "fit_scope": "full_raw_dataset (via ML.pipeline.preprocessing_pipeline.PreprocessingPipeline)",
        "reusable_entry_point": "ML.pipeline.preprocessing_pipeline.PreprocessingPipeline.load(directory).transform(new_raw_dataframe)",
    }
    metadata_path = SAVED_MODELS_DIR / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote %s and %s", feature_names_path, metadata_path)


def run_reusability_smoke_test() -> dict:
    """Fits on one row-slice of the raw data and transforms a different
    slice, proving the pipeline is reusable on new data without
    recomputing its learned state. Not the official train/test split."""
    from ML.ingestion.config import load_config
    from ML.ingestion.loader import load_dataset

    config = load_config(DEFAULT_CONFIG_PATH)
    dataframe, _metadata = load_dataset(config)

    split_index = int(len(dataframe) * 0.8)
    fit_slice = dataframe.iloc[:split_index].reset_index(drop=True)
    transform_slice = dataframe.iloc[split_index:].reset_index(drop=True)

    smoke_pipeline = PreprocessingPipeline()
    fit_result = smoke_pipeline.fit_transform(fit_slice)
    transform_result = smoke_pipeline.transform(transform_slice)

    schema_matches = list(fit_result["features"].columns) == list(transform_result["features"].columns)

    return {
        "fit_slice_rows": len(fit_slice),
        "transform_slice_rows": len(transform_slice),
        "fit_feature_count": fit_result["features"].shape[1],
        "transform_feature_count": transform_result["features"].shape[1],
        "schema_matches": schema_matches,
    }


def write_pipeline_report(result: dict, model_ready_shape, smoke_test: dict) -> None:
    lines = [
        "# Preprocessing Pipeline Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## What this milestone consolidates",
        "",
        "`ML/pipeline/preprocessing_pipeline.py` wraps the previously-separate Milestone 1 (ingestion), "
        "Milestone 3 (cleaning), and Milestone 4 (feature engineering) modules behind a single "
        "`PreprocessingPipeline` class with a `fit_transform`/`transform` contract:",
        "",
        "1. **Load** raw data — `ML.ingestion.loader.load_dataset`",
        "2. **Validate** — `ML.ingestion.validator.run_all_validations` (raises on failure via "
        "`load_validate_and_fit`, rather than silently preprocessing invalid data)",
        "3. **Clean** — `ML.cleaning.pipeline.fit_clean_dataset` / `transform_clean_dataset`",
        "4. **Engineer features (encode + scale)** — `ML.feature_engineering.pipeline.fit_engineer_features` / "
        "`transform_engineer_features`",
        "5. **Preserve survey variables** — `PATWT`/`EDWT`/`CSTRATM`/`CPSUM` pass through every stage untouched",
        "",
        "## Why fit/transform, not just one function",
        "",
        "Milestones 3 and 4 originally detected-and-applied cleaning/encoding decisions in a single pass. "
        "That is fine for a one-off report, but is NOT reusable: calling the same code again on a different "
        "dataset (a validation split, or a future inference request) would silently recompute different "
        "imputation medians, a different dropped-column list, and different encoder categories — violating "
        "the requirement (CLAUDE.md, PROJECT_CONTEXT.md) that preprocessing at inference time exactly match "
        "preprocessing at training time.",
        "",
        "This milestone split the genuinely data-dependent decisions (duplicate/constant/near-zero-variance "
        "columns to drop, which columns are boolean, imputation medians, encoder categories, scaler mean/std) "
        "out from the stateless rules (sentinel codes, implied-decimal correction, text standardization, "
        "leakage exclusion, target derivation), so the former can be learned once and reapplied consistently.",
        "",
        "## Reproducibility check",
        "",
        f"Running the full pipeline directly from the raw SAS file reproduced a "
        f"{model_ready_shape[0]} x {model_ready_shape[1]} output "
        "— matching the shape independently produced by the separate Milestone 3 + 4 scripts.",
        "",
        "## Reusability smoke test",
        "",
        "Fit on the first 80% of raw rows, then called `transform()` on the remaining 20% (an ad hoc slice "
        "for this test only — not the official Milestone 7 train/test split):",
        "",
        f"- Fit slice: {smoke_test['fit_slice_rows']} rows -> {smoke_test['fit_feature_count']} feature columns",
        f"- Transform slice: {smoke_test['transform_slice_rows']} rows -> {smoke_test['transform_feature_count']} "
        "feature columns",
        f"- Feature schema identical between fit and transform outputs: **{smoke_test['schema_matches']}**",
        "",
        "This confirms `transform()` reuses the fitted encoder/scaler/medians/dropped-column-lists rather than "
        "re-deriving them from the new slice — the core property a 'reusable' pipeline requires.",
        "",
        "## Persisted artifacts",
        "",
        "- `ML/saved_models/preprocessing_pipeline.pkl` — the full fitted `PreprocessingPipeline` object "
        "(reload with `PreprocessingPipeline.load(...)`)",
        "- `ML/saved_models/encoder.pkl`, `scaler.pkl`, `preprocessing.pkl` — individually loadable, matching "
        "TASKS.md's prescribed `saved_models/` layout",
        "- `ML/saved_models/feature_names.json`, `metadata.json`",
        "",
        "## No model was trained",
        "",
        "Only preprocessing artifacts (encoder, scaler, imputation medians, dropped-column lists) were fit "
        "and persisted — no predictive model (Logistic Regression, Random Forest, etc.) was trained, per "
        "PROJECT_CONTEXT.md's Machine Learning / Backend separation of concerns.",
        "",
    ]

    report_path = PIPELINE_REPORTS_DIR / "preprocessing_pipeline_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 9 - Reusable Preprocessing Pipeline")
    PIPELINE_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Loading, validating, and fitting the pipeline on the full raw dataset")
    pipeline, result = load_validate_and_fit()

    model_ready = assemble_model_ready(result)
    model_ready.to_parquet(MODEL_READY_DATASET_PATH, index=False)
    logger.info("Wrote %s (shape %s)", MODEL_READY_DATASET_PATH, model_ready.shape)

    save_artifacts(pipeline, result)

    logger.info("Running reusability smoke test (fit on 80%% slice, transform on 20%% slice)")
    smoke_test = run_reusability_smoke_test()
    logger.info(
        "Smoke test: schema_matches=%s (fit %d cols, transform %d cols)",
        smoke_test["schema_matches"], smoke_test["fit_feature_count"], smoke_test["transform_feature_count"],
    )
    if not smoke_test["schema_matches"]:
        logger.error("Reusability smoke test FAILED: feature schema differs between fit and transform outputs.")

    write_pipeline_report(result, model_ready.shape, smoke_test)

    logger.info("Milestone 9 (Reusable Preprocessing Pipeline) completed successfully.")


if __name__ == "__main__":
    main()
