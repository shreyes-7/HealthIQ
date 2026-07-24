"""Milestone 4 - Feature Engineering.

Loads the cleaned dataset, derives the prediction target, excludes
leakage/facility-level/identifier/sparse-redundant variables, removes
near-duplicate and near-zero-variance columns, encodes categoricals,
scales continuous variables, and saves the result plus reusable
preprocessing artifacts. No model is trained.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_feature_engineering
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd

from ML.feature_engineering.pipeline import SPARSE_REDUNDANT_VARIABLES, fit_engineer_features
from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CLEANED_DATASET_PATH = resolve_repo_path("Data/processed/ed2022_cleaned.parquet")
MODEL_READY_DATASET_PATH = resolve_repo_path("Data/processed/ed2022_model_ready.parquet")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
FEATURE_ENGINEERING_REPORTS_DIR = resolve_repo_path("ML/reports/feature_engineering")


def build_feature_roles(result: dict, raw_columns: list[str]) -> dict:
    fitted_state = result["fitted_state"]
    roles = {}
    for column in raw_columns:
        if column in ("ADMITHOS", "OBSHOS"):
            roles[column] = "consumed_for_target"
        elif column in result["survey"].columns:
            roles[column] = "preserved_survey_variable"
        elif column in result["identifiers"].columns:
            roles[column] = "excluded_identifier_kept_for_traceability"
        elif column in SPARSE_REDUNDANT_VARIABLES:
            roles[column] = "excluded_sparse_redundant"
        elif column in fitted_state["excluded_columns"]:
            roles[column] = "excluded_leakage_or_facility_level"
        elif column in fitted_state["continuous_columns"]:
            roles[column] = "scaled_continuous_feature"
        elif column not in fitted_state["categorical_columns"] and column not in fitted_state["continuous_columns"]:
            roles[column] = "removed_redundant_or_near_zero_variance"
        else:
            roles[column] = "encoded_categorical_feature"
    return roles


def write_feature_engineering_report(raw_shape, result: dict) -> None:
    log = result["log"]
    fitted_state = result["fitted_state"]
    exclude_entry = next(e for e in log.entries if e["action"] == "excluded_leakage_identifier_survey_and_sparse_columns")
    rfv_entry = next((e for e in log.entries if e["action"] == "dropped_near_duplicate_rfv_codes"), None)
    nzv_entry = next((e for e in log.entries if e["action"] == "dropped_near_zero_variance_columns"), None)
    final_entry = next(e for e in log.entries if e["action"] == "built_final_feature_matrix")

    encoder_metadata = fitted_state["encoder"].get_feature_metadata()
    one_hot_count = sum(1 for v in encoder_metadata.values() if v["encoding"] == "one_hot")
    frequency_count = sum(1 for v in encoder_metadata.values() if v["encoding"] == "frequency")

    lines = [
        "# Feature Engineering Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Input (cleaned) shape: {raw_shape[0]} rows x {raw_shape[1]} columns",
        f"- Output feature matrix: {result['features'].shape[0]} rows x {result['features'].shape[1]} columns",
        f"- Target column: `{TARGET_COLUMN_NAME}` (derived from `ADMITHOS`/`OBSHOS`, both removed from features)",
        f"- Output file: `Data/processed/ed2022_model_ready.parquet`",
        f"- No model was trained. Cleaned dataset (`ed2022_cleaned.parquet`) and raw dataset were not modified.",
        "",
        "## 1. Leakage, Facility-Level, and Identifier Exclusion",
        "",
        f"{exclude_entry['count']} columns excluded from the feature set before encoding:",
        "",
        "- **Disposition block** (16 vars) and **post-admission hospital course** (14 vars): these describe "
        "the admission decision itself or its downstream consequences (which unit, length of stay, discharge "
        "diagnosis, boarding time) — using them as predictors would leak the answer into the input.",
        "- **Facility-level questionnaire items** (16 vars): hospital-level policy/staffing questions "
        "(ambulance diversion, bed coordinators), not per-visit clinical data.",
        "- **Identifiers** (`HOSPCODE`, `PATCODE`): kept in the output for traceability but excluded from "
        "the feature matrix — an ID number is never a valid predictor.",
        "- **Survey variables** (`PATWT`, `EDWT`, `CSTRATM`, `CPSUM`): preserved untouched in the output, "
        "excluded from the feature matrix — see Milestone 1/3 for why.",
        "- **`AGEDAYS`**: legitimate pre-decision variable but 97%+ missing outside the infant subgroup and "
        "largely redundant with `AGE`.",
        "",
        "Full list: `ML/reports/feature_engineering/feature_roles.json`.",
        "",
        "## 2. Redundant Variable Removal",
        "",
    ]
    if rfv_entry:
        lines.append(
            f"- Dropped `{rfv_entry['columns']}` (correlation 1.0 with their `*3D` recode per Milestone 2 EDA); "
            "kept the coarser 3-digit recode for tractable, interpretable encoding."
        )
    if nzv_entry:
        lines.append(
            f"- Dropped {nzv_entry['count']} near-zero-variance categorical columns (dominant category >= "
            f"{int(nzv_entry['threshold'] * 100)}% of visits — mostly rarely-used medication-slot fields). "
            "Full list in `feature_roles.json`. More rigorous, target-aware feature selection is deferred to "
            "Milestone 6."
        )

    lines += [
        "",
        "## 3. Categorical Encoding",
        "",
        f"- One-hot encoded (<= {fitted_state['encoder'].one_hot_max_categories} categories): {one_hot_count} "
        "variables (most-frequent category dropped as reference to avoid the dummy-variable trap)",
        f"- Frequency encoded (> {fitted_state['encoder'].one_hot_max_categories} categories): {frequency_count} "
        "variables (diagnosis/drug/arrival-time codes — one-hot would add thousands of near-empty columns)",
        "",
        "## 4. Numerical Scaling",
        "",
        f"- Z-score standardized: {len(fitted_state['continuous_columns'])} continuous variables "
        f"({sorted(fitted_state['continuous_columns'])})",
        "- Not applied to encoded categorical/boolean columns (they remain 0/1 indicators).",
        "- Tree-based models (Random Forest, XGBoost, LightGBM, CatBoost) do not require scaling; it is "
        "provided for Logistic Regression and saved as a reusable artifact. Raw values remain available in "
        "`ed2022_cleaned.parquet`; mean/std per column are in `ML/saved_models/metadata.json` for "
        "inverse-transform.",
        "",
        "## 5. Final Feature Matrix",
        "",
        f"- {final_entry['feature_count']} total feature columns "
        f"({final_entry['continuous_source_count']} scaled continuous + encoded categoricals)",
        "",
        "## 6. Reproducibility Caveat",
        "",
        "The encoder and scaler in this milestone are fit on the **full** cleaned dataset, because Milestone 7 "
        "(Train/Test Split) had not yet run when this script was first written. Milestone 9's "
        "`ML/pipeline/preprocessing_pipeline.py` now exposes a proper `fit`/`transform` contract so the same "
        "encoder/scaler can be refit on a training split only and reapplied to test/inference data without "
        "leaking test-set statistics — see that module for the reusable entry point.",
        "",
    ]

    report_path = FEATURE_ENGINEERING_REPORTS_DIR / "feature_engineering_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 4 - Feature Engineering")
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    FEATURE_ENGINEERING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if not CLEANED_DATASET_PATH.exists():
        logger.error("Cleaned dataset not found at %s. Run Milestone 3 (run_cleaning) first.", CLEANED_DATASET_PATH)
        return

    dataframe = pd.read_parquet(CLEANED_DATASET_PATH)
    logger.info("Loaded cleaned dataset with shape %s", dataframe.shape)

    result = fit_engineer_features(dataframe)
    fitted_state = result["fitted_state"]
    logger.info(
        "Feature engineering complete: %d target + %d features + %d survey + %d identifier columns",
        1, result["features"].shape[1], result["survey"].shape[1], result["identifiers"].shape[1],
    )

    model_ready = pd.concat(
        [result["target"], result["features"], result["survey"], result["identifiers"]], axis=1
    )
    model_ready.to_parquet(MODEL_READY_DATASET_PATH, index=False)
    logger.info("Wrote %s (shape %s)", MODEL_READY_DATASET_PATH, model_ready.shape)

    joblib.dump(fitted_state["encoder"], SAVED_MODELS_DIR / "encoder.pkl")
    joblib.dump(fitted_state["scaler"], SAVED_MODELS_DIR / "scaler.pkl")
    joblib.dump(
        {"encoder": fitted_state["encoder"], "scaler": fitted_state["scaler"]},
        SAVED_MODELS_DIR / "preprocessing.pkl",
    )
    logger.info("Wrote encoder.pkl, scaler.pkl, preprocessing.pkl to %s", SAVED_MODELS_DIR)

    feature_names_path = SAVED_MODELS_DIR / "feature_names.json"
    feature_names_path.write_text(json.dumps(list(result["features"].columns), indent=2), encoding="utf-8")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_column": TARGET_COLUMN_NAME,
        "feature_count": int(result["features"].shape[1]),
        "continuous_columns": fitted_state["continuous_columns"],
        "categorical_source_columns": fitted_state["categorical_columns"],
        "excluded_columns": fitted_state["excluded_columns"],
        "survey_columns": list(result["survey"].columns),
        "identifier_columns": list(result["identifiers"].columns),
        "encoder_feature_metadata": fitted_state["encoder"].get_feature_metadata(),
        "scaler_feature_metadata": fitted_state["scaler"].get_feature_metadata(),
        "fit_scope": "full_cleaned_dataset (see ML/pipeline/preprocessing_pipeline.py for the fit/transform-capable entry point)",
    }
    metadata_path = SAVED_MODELS_DIR / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote %s and %s", feature_names_path, metadata_path)

    feature_roles = build_feature_roles(result, list(dataframe.columns))
    roles_path = FEATURE_ENGINEERING_REPORTS_DIR / "feature_roles.json"
    roles_path.write_text(json.dumps(feature_roles, indent=2), encoding="utf-8")
    logger.info("Wrote %s", roles_path)

    write_feature_engineering_report(dataframe.shape, result)

    logger.info("Milestone 4 (Feature Engineering) completed successfully.")


if __name__ == "__main__":
    main()
