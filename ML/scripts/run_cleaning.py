"""Milestone 3 - Data Cleaning.

Loads the raw NHAMCS dataset, cleans it according to the documented,
per-variable rules in ML/cleaning/, and saves the result as a separate
artifact. The raw dataset is never modified.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_cleaning
"""

import json
import logging
from collections import Counter
from datetime import datetime, timezone

from ML.cleaning.pipeline import fit_clean_dataset
from ML.cleaning.variable_roles import (
    CONDITIONAL_NUMERICAL_VARIABLES,
    CONTINUOUS_NUMERICAL_VARIABLES,
    IDENTIFIER_VARIABLES,
    NOMINAL_CODE_VARIABLES,
    SURVEY_VARIABLES,
)
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CLEANING_REPORTS_DIR = resolve_repo_path("ML/reports/cleaning")
PROCESSED_DATA_DIR = resolve_repo_path("Data/processed")
CLEANED_DATASET_PATH = PROCESSED_DATA_DIR / "ed2022_cleaned.parquet"


def build_column_roles(cleaned_columns: list[str], boolean_columns: list[str]) -> dict:
    roles = {}
    for column in cleaned_columns:
        if column in SURVEY_VARIABLES:
            roles[column] = "survey_design"
        elif column in IDENTIFIER_VARIABLES:
            roles[column] = "identifier"
        elif column in CONTINUOUS_NUMERICAL_VARIABLES:
            roles[column] = "continuous_numerical"
        elif column in CONDITIONAL_NUMERICAL_VARIABLES:
            roles[column] = "conditional_numerical_not_imputed"
        elif column in NOMINAL_CODE_VARIABLES:
            roles[column] = "nominal_code_categorical"
        elif column in boolean_columns:
            roles[column] = "boolean_categorical"
        else:
            roles[column] = "generic_categorical"
    return roles


def write_cleaning_report(raw_shape, cleaned_dataframe, log, column_roles) -> None:
    entries = log.entries
    step_counts = Counter(entry["step"] for entry in entries)

    duplicate_row_entry = next((e for e in entries if e["step"] == "remove_duplicate_rows"), None)
    duplicate_column_entries = log.entries_for_step("remove_duplicate_columns")
    constant_column_entry = next((e for e in entries if e["step"] == "remove_constant_columns"), None)
    sentinel_entries = log.entries_for_step("sentinel_to_nan")
    annotation_entries = log.entries_for_step("non_numeric_annotation_to_nan")
    decimal_entries = log.entries_for_step("implied_decimal_correction")
    median_impute_entries = [e for e in log.entries_for_step("impute_missing_values") if e["action"] == "median_imputed"]
    category_impute_entries = [
        e for e in log.entries_for_step("impute_missing_values") if e["action"] == "filled_with_missing_category"
    ]
    conditional_skip_entries = [
        e for e in log.entries_for_step("impute_missing_values")
        if e["action"] == "left_as_nan_conditionally_not_applicable"
    ]

    remaining_nan_counts = cleaned_dataframe.isna().sum()
    remaining_nan_counts = remaining_nan_counts[remaining_nan_counts > 0].sort_values(ascending=False)

    lines = [
        "# Data Cleaning Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Raw shape: {raw_shape[0]} rows x {raw_shape[1]} columns",
        f"- Cleaned shape: {cleaned_dataframe.shape[0]} rows x {cleaned_dataframe.shape[1]} columns",
        f"- Output: `Data/processed/ed2022_cleaned.parquet`",
        f"- Raw file (`Data/raw/ed2022_sas.sas7bdat`) was not modified.",
        "",
        "## 1. Duplicate Removal",
        "",
        f"- Duplicate rows removed: {duplicate_row_entry['count'] if duplicate_row_entry else 0}",
        f"- Duplicate columns removed: {len(duplicate_column_entries)}"
        + (f" ({', '.join(e['column'] + ' (dup of ' + e['duplicate_of'] + ')' for e in duplicate_column_entries)})"
           if duplicate_column_entries else ""),
        "",
        "## 2. Constant Column Removal",
        "",
        f"- Constant (single-value) columns removed: {constant_column_entry['count'] if constant_column_entry else 0}",
        "",
        "## 3. Sentinel / Invalid Value Handling",
        "",
        "NHAMCS encodes Not-applicable (-7), Unknown (-8), and Blank (-9) as "
        "sentinel codes rather than true NaN, in both numeric and string-typed "
        "columns (confirmed by a full-dataset scan; no other negative codes or "
        "blank strings exist). All were converted to proper NaN.",
        "",
        f"- Columns with sentinel codes converted: {len(sentinel_entries)}",
        f"- Total sentinel values converted to NaN: {sum(e['count'] for e in sentinel_entries)}",
        "",
        "Codebook-documented non-numeric annotation codes were also converted "
        "to NaN (e.g. `PULSE`/`PULSED` == 998 means \"measured by Doppler\", not "
        "a heart rate of 998; same for `BPDIAS`/`BPDIASD`):",
        "",
    ]
    for entry in annotation_entries:
        lines.append(f"- `{entry['column']}`: {entry['count']} annotation code(s) ({entry['codes']}) converted to NaN")

    lines += [
        "",
        "## 4. Implied-Decimal Corrections",
        "",
        "The codebook documents an implied decimal for these variables (e.g. "
        "`TEMPF` raw value 986 means 98.6°F; `RFV1-5` raw codes are the real "
        "code x10). Values were divided by 10 accordingly:",
        "",
    ]
    for entry in decimal_entries:
        lines.append(f"- `{entry['column']}`: {entry['count']} value(s) corrected")

    lines += [
        "",
        "## 5. Data Type Corrections",
        "",
        "- Genuine 0/1 flags converted to a 2-level \"No\"/\"Yes\" category.",
        "- Identifier columns (`HOSPCODE`, `PATCODE`) converted to nullable Int64; never treated as a measurement.",
        "- Whole-number continuous/conditional variables converted to nullable Int64; decimal measurements "
        "(`TEMPF`, `TEMPDF`, RFV codes) remain float64.",
        "- RFV nominal codes converted to category dtype (median imputation on a classification code is meaningless).",
        "- All remaining generic categorical columns converted to category dtype.",
        "",
        "## 6. Missing Value Imputation",
        "",
        f"- Continuous numerical variables median-imputed: {len(median_impute_entries)}",
    ]
    for entry in median_impute_entries:
        lines.append(f"  - `{entry['column']}`: {entry['count']} value(s) filled with median {entry['median_value']}")

    lines += [
        "",
        "- Conditional numerical variables deliberately left as NaN (value does not conceptually apply to most rows):",
    ]
    for entry in conditional_skip_entries:
        lines.append(f"  - `{entry['column']}`: {entry['count']} NaN remaining (not imputed) — {entry['reason']}")

    lines += [
        "",
        f"- Categorical columns filled with an explicit \"Missing\" category: {len(category_impute_entries)}",
        "  (chosen over mode-imputation so unknown/blank/not-applicable remains visible to downstream models "
        "rather than being folded into the majority class)",
        "",
        "## 7. Survey Variables",
        "",
        f"`{sorted(SURVEY_VARIABLES)}` were never touched by any step above — preserved exactly as in the raw "
        "dataset for the survey-aware learning workflow.",
        "",
        "## 8. Remaining Missing Values",
        "",
        "After cleaning, missing values remain only in conditional numerical variables (by design) and "
        "`EDWT` (genuine facility non-participation, not sentinel-coded — see Milestone 1).",
        "",
    ]
    if not remaining_nan_counts.empty:
        for column, count in remaining_nan_counts.items():
            lines.append(f"- `{column}`: {count} ({round(count / len(cleaned_dataframe) * 100, 2)}%)")
    else:
        lines.append("- None.")

    report_path = CLEANING_REPORTS_DIR / "cleaning_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 3 - Data Cleaning")
    CLEANING_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config(DEFAULT_CONFIG_PATH)

    try:
        dataframe, metadata = load_dataset(config)
    except FileNotFoundError as error:
        logger.error("Cleaning aborted: %s", error)
        return

    raw_shape = dataframe.shape
    cleaned_dataframe, log, _fitted_state = fit_clean_dataset(dataframe)
    logger.info("Cleaned shape: %s (from raw %s)", cleaned_dataframe.shape, raw_shape)

    boolean_columns = [
        entry["column"] for entry in log.entries_for_step("dtype_correction")
        if entry["action"] == "converted_to_boolean_category"
    ]
    column_roles = build_column_roles(list(cleaned_dataframe.columns), boolean_columns)

    cleaned_dataframe.to_parquet(CLEANED_DATASET_PATH, index=False)
    logger.info("Wrote cleaned dataset to %s", CLEANED_DATASET_PATH)

    log_path = CLEANING_REPORTS_DIR / "transformation_log.json"
    log_path.write_text(json.dumps(log.entries, indent=2, default=str), encoding="utf-8")
    logger.info("Wrote %s (%d entries)", log_path, len(log.entries))

    roles_path = CLEANING_REPORTS_DIR / "column_roles.json"
    roles_path.write_text(json.dumps(column_roles, indent=2), encoding="utf-8")
    logger.info("Wrote %s", roles_path)

    write_cleaning_report(raw_shape, cleaned_dataframe, log, column_roles)

    logger.info("Milestone 3 (Data Cleaning) completed successfully.")


if __name__ == "__main__":
    main()
