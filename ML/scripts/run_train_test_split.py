"""Milestone 7 - Train/Test Preparation.

Splits the raw dataset into stratified train/validation/test row sets,
then fits the PreprocessingPipeline on the TRAINING split only and
transforms validation/test with that same fitted state. This resolves
the "fit on full dataset" caveat documented throughout Milestones 4/5/9/10:
from this point on, `ML/saved_models/` holds artifacts fit on training
data only, ready for Phase 2 model development.

No model is trained here -- only the preprocessing pipeline is fit.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_train_test_split
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset
from ML.ingestion.validator import run_all_validations
from ML.pipeline.dataset_split import (
    RANDOM_STATE,
    TEST_FRACTION,
    TRAIN_FRACTION,
    VALIDATION_FRACTION,
    stratified_train_validation_test_split,
)
from ML.pipeline.preprocessing_pipeline import PreprocessingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = resolve_repo_path("Data/processed")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
SPLIT_REPORTS_DIR = resolve_repo_path("ML/reports/split")


def assemble_split_dataframe(result: dict) -> pd.DataFrame:
    return pd.concat([result["target"], result["features"], result["survey"], result["identifiers"]], axis=1)


def class_balance(target: pd.Series) -> dict:
    counts = target.value_counts().sort_index()
    percentages = (counts / len(target) * 100).round(2)
    return {"counts": counts.to_dict(), "percentages": percentages.to_dict()}


def write_split_report(splits_raw: dict, split_results: dict, split_frames: dict) -> None:
    lines = [
        "# Train/Test Preparation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"Split ratios: train {int(TRAIN_FRACTION*100)}% / validation {int(VALIDATION_FRACTION*100)}% / "
        f"test {int(TEST_FRACTION*100)}%, stratified by the prediction target, random_state={RANDOM_STATE}.",
        "",
        "The split happens on the RAW dataset, before cleaning or feature engineering. The "
        "PreprocessingPipeline is fit ONLY on the training split; validation and test are "
        "transformed using that fitted state (learned imputation medians, dropped-column "
        "decisions, encoder categories, scaler mean/std) — never re-derived from validation/test "
        "data. This is what makes the split methodologically valid: no information from held-out "
        "rows leaks into how the training data was preprocessed.",
        "",
        "## Split sizes and class balance",
        "",
        "| Split | Rows | Not Admitted | Admitted | % Admitted |",
        "|---|---|---|---|---|",
    ]
    for split_name in ("train", "validation", "test"):
        target = split_results[split_name]["target"]
        balance = class_balance(target)
        not_admitted = balance["counts"].get(0, 0)
        admitted = balance["counts"].get(1, 0)
        pct = balance["percentages"].get(1, 0.0)
        lines.append(f"| {split_name} | {len(target)} | {not_admitted} | {admitted} | {pct}% |")

    feature_columns = {name: list(result["features"].columns) for name, result in split_results.items()}
    schema_matches = feature_columns["train"] == feature_columns["validation"] == feature_columns["test"]

    lines += [
        "",
        f"Feature schema identical across all three splits: **{schema_matches}** "
        f"({len(feature_columns['train'])} feature columns).",
        "",
        "## Output files",
        "",
        "- `Data/processed/train.parquet`",
        "- `Data/processed/validation.parquet`",
        "- `Data/processed/test.parquet`",
        "- `ML/saved_models/preprocessing_pipeline.pkl`, `encoder.pkl`, `scaler.pkl`, `preprocessing.pkl`, "
        "`feature_names.json`, `metadata.json` — all now fit on the **training split only** "
        "(superseding the full-dataset-fit versions produced in Milestones 4/5/9).",
        "",
        "## No model was trained",
        "",
        "Only the preprocessing pipeline (cleaning + feature engineering state) was fit on the "
        "training split. No predictive model was trained or evaluated.",
        "",
    ]

    report_path = SPLIT_REPORTS_DIR / "train_test_split_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 7 - Train/Test Preparation")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    SPLIT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config(DEFAULT_CONFIG_PATH)
    dataframe, _metadata = load_dataset(config)

    validation_checks = run_all_validations(dataframe, config)
    failed_checks = [check.name for check in validation_checks if not check.passed]
    if failed_checks:
        logger.error("Aborting: dataset validation failed: %s", failed_checks)
        return

    splits_raw = stratified_train_validation_test_split(dataframe)
    logger.info(
        "Split sizes: train=%d, validation=%d, test=%d",
        len(splits_raw["train"]), len(splits_raw["validation"]), len(splits_raw["test"]),
    )

    pipeline = PreprocessingPipeline()
    split_results = {"train": pipeline.fit_transform(splits_raw["train"])}
    split_results["validation"] = pipeline.transform(splits_raw["validation"])
    split_results["test"] = pipeline.transform(splits_raw["test"])
    logger.info("Fit pipeline on training split; transformed validation and test splits")

    split_frames = {}
    for split_name, result in split_results.items():
        frame = assemble_split_dataframe(result)
        split_frames[split_name] = frame
        output_path = PROCESSED_DATA_DIR / f"{split_name}.parquet"
        frame.to_parquet(output_path, index=False)
        logger.info("Wrote %s (shape %s)", output_path, frame.shape)

    pipeline_path = pipeline.save(SAVED_MODELS_DIR)
    joblib.dump(pipeline.encoder, SAVED_MODELS_DIR / "encoder.pkl")
    joblib.dump(pipeline.scaler, SAVED_MODELS_DIR / "scaler.pkl")
    joblib.dump({"encoder": pipeline.encoder, "scaler": pipeline.scaler}, SAVED_MODELS_DIR / "preprocessing.pkl")
    logger.info("Wrote %s and refreshed encoder.pkl/scaler.pkl/preprocessing.pkl (fit on training split only)", pipeline_path)

    train_features = split_results["train"]["features"]
    feature_names_path = SAVED_MODELS_DIR / "feature_names.json"
    feature_names_path.write_text(json.dumps(list(train_features.columns), indent=2), encoding="utf-8")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_column": TARGET_COLUMN_NAME,
        "feature_count": int(train_features.shape[1]),
        "split_ratios": {"train": TRAIN_FRACTION, "validation": VALIDATION_FRACTION, "test": TEST_FRACTION},
        "random_state": RANDOM_STATE,
        "split_sizes": {name: len(frame) for name, frame in split_frames.items()},
        "encoder_feature_metadata": pipeline.encoder.get_feature_metadata(),
        "scaler_feature_metadata": pipeline.scaler.get_feature_metadata(),
        "fit_scope": "training_split_only (Milestone 7) — no test-set leakage into preprocessing statistics",
    }
    metadata_path = SAVED_MODELS_DIR / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote %s and %s (fit_scope: training_split_only)", feature_names_path, metadata_path)

    write_split_report(splits_raw, split_results, split_frames)

    logger.info("Milestone 7 (Train/Test Preparation) completed successfully.")


if __name__ == "__main__":
    main()
