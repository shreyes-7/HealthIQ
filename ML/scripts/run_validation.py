"""Milestone 11 - Validation.

Verifies the preprocessing pipeline's output is correct: no unexpected
missing values, correct datatypes, matching feature dimensions across
splits, and deterministic reproducibility. Automated unit tests for the
individual modules live in ML/tests/ (run with `pytest ML/tests`).

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_validation
"""

import logging
from datetime import datetime, timezone

import pandas as pd

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset
from ML.pipeline.preprocessing_pipeline import PreprocessingPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DATA_DIR = resolve_repo_path("Data/processed")
VALIDATION_REPORTS_DIR = resolve_repo_path("ML/reports/validation")
NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}
SPLIT_NAMES = ("train", "validation", "test")


def load_splits() -> dict:
    return {name: pd.read_parquet(PROCESSED_DATA_DIR / f"{name}.parquet") for name in SPLIT_NAMES}


def check_no_missing_values_in_features(splits: dict) -> dict:
    results = {}
    for name, frame in splits.items():
        feature_columns = [c for c in frame.columns if c not in NON_FEATURE_COLUMNS]
        missing_count = int(frame[feature_columns].isna().sum().sum())
        results[name] = {"passed": missing_count == 0, "missing_cells": missing_count}
    return results


def check_correct_datatypes(splits: dict) -> dict:
    results = {}
    for name, frame in splits.items():
        feature_columns = [c for c in frame.columns if c not in NON_FEATURE_COLUMNS]
        non_numeric = [c for c in feature_columns if not pd.api.types.is_numeric_dtype(frame[c])]
        results[name] = {"passed": len(non_numeric) == 0, "non_numeric_columns": non_numeric}
    return results


def check_matching_dimensions(splits: dict) -> dict:
    feature_column_sets = {
        name: sorted(c for c in frame.columns if c not in NON_FEATURE_COLUMNS) for name, frame in splits.items()
    }
    reference = feature_column_sets["train"]
    matches = {name: (columns == reference) for name, columns in feature_column_sets.items()}
    return {
        "passed": all(matches.values()),
        "per_split_matches_train": matches,
        "feature_count": len(reference),
    }


def check_reproducibility() -> dict:
    """Fits the pipeline twice on the same small raw slice and confirms
    numerically identical output -- the pipeline must be deterministic."""
    config = load_config(DEFAULT_CONFIG_PATH)
    dataframe, _metadata = load_dataset(config)
    sample = dataframe.head(500).reset_index(drop=True)

    result_a = PreprocessingPipeline().fit_transform(sample)
    result_b = PreprocessingPipeline().fit_transform(sample)

    features_match = result_a["features"].equals(result_b["features"])
    target_match = result_a["target"].equals(result_b["target"])

    return {"passed": features_match and target_match, "features_match": features_match, "target_match": target_match}


def write_validation_report(checks: dict) -> bool:
    all_passed = all(check["passed"] for check in checks.values())

    lines = [
        "# Validation Report (Milestone 11)",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## Overall: {'PASS' if all_passed else 'FAIL'}",
        "",
    ]
    for check_name, result in checks.items():
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"### [{status}] {check_name}")
        lines.append("")
        lines.append("```")
        lines.append(str(result))
        lines.append("```")
        lines.append("")

    lines += [
        "## Pipeline unit tests",
        "",
        "Automated unit tests for the individual modules (sentinel handling, leakage exclusion, "
        "encoder/scaler fit-transform correctness, derived features, cleaning/feature-engineering "
        "fit-vs-transform consistency) are in `ML/tests/` — run with `pytest ML/tests`.",
        "",
    ]

    report_path = VALIDATION_REPORTS_DIR / "validation_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)
    return all_passed


def main() -> None:
    logger.info("Starting Milestone 11 - Validation")
    VALIDATION_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    missing = [name for name in SPLIT_NAMES if not (PROCESSED_DATA_DIR / f"{name}.parquet").exists()]
    if missing:
        logger.error("Missing split file(s) %s. Run Milestone 7 (run_train_test_split) first.", missing)
        return

    splits = load_splits()

    checks = {
        "no_missing_values_in_features": {
            "passed": all(r["passed"] for r in check_no_missing_values_in_features(splits).values()),
            "detail": check_no_missing_values_in_features(splits),
        },
        "correct_datatypes": {
            "passed": all(r["passed"] for r in check_correct_datatypes(splits).values()),
            "detail": check_correct_datatypes(splits),
        },
        "correct_feature_dimensions": check_matching_dimensions(splits),
        "pipeline_reproducibility": check_reproducibility(),
    }

    for name, result in checks.items():
        logger.info("[%s] %s", "PASS" if result["passed"] else "FAIL", name)

    all_passed = write_validation_report(checks)

    if all_passed:
        logger.info("Milestone 11 (Validation) completed successfully. All checks PASSED.")
    else:
        logger.error("Milestone 11 (Validation) completed with FAILURES. See validation_report.md.")


if __name__ == "__main__":
    main()
