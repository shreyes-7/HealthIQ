"""Milestone 1 - Dataset Setup.

Loads the raw NHAMCS dataset, validates it, identifies the target and
survey design variables, and generates a data dictionary. Produces reports
only: the raw dataset is never modified, and no cleaning is performed.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_dataset_setup
"""

import json
import logging
from datetime import datetime, timezone

from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.data_dictionary import build_data_dictionary
from ML.ingestion.loader import load_dataset
from ML.ingestion.validator import run_all_validations

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

REPORTS_DIR = resolve_repo_path("ML/reports")


def write_dataset_report(dataframe, metadata, config) -> None:
    dtype_counts = dataframe.dtypes.astype(str).value_counts().to_dict()
    labeled_column_count = sum(1 for label in metadata.column_names_to_labels.values() if label)

    lines = [
        "# Dataset Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Source file: `{config['dataset']['raw_path']}`",
        f"- File encoding: {metadata.file_encoding}",
        f"- Rows: {dataframe.shape[0]}",
        f"- Columns: {dataframe.shape[1]}",
        f"- Columns with a descriptive label: {labeled_column_count} / {dataframe.shape[1]}",
        "",
        "## Column dtype breakdown",
        "",
    ]
    for dtype, count in dtype_counts.items():
        lines.append(f"- {dtype}: {count}")

    report_path = REPORTS_DIR / "dataset_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def write_dataset_metadata_json(dataframe, metadata, config) -> None:
    metadata_record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": config["dataset"]["raw_path"],
        "file_encoding": metadata.file_encoding,
        "row_count": int(dataframe.shape[0]),
        "column_count": int(dataframe.shape[1]),
        "target_variables": [
            config["target"]["admitted_to_hospital_flag"],
            config["target"]["admitted_via_observation_flag"],
        ],
        "derived_target_name": config["target"]["derived_target_name"],
        "survey_design_variables": [
            config["survey_design"]["weight_variable"],
            config["survey_design"]["strata_variable"],
            config["survey_design"]["cluster_variable"],
        ],
        "facility_weight_variable": config["survey_design"]["facility_weight_variable"],
    }

    report_path = REPORTS_DIR / "dataset_metadata.json"
    report_path.write_text(json.dumps(metadata_record, indent=2), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def write_validation_report(checks) -> None:
    lines = ["# Validation Report", "", f"Generated: {datetime.now(timezone.utc).isoformat()}", ""]

    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"## [{status}] {check.name}")
        lines.append("")
        lines.append(check.message)
        if check.details:
            lines.append("")
            lines.append("```")
            lines.append(json.dumps(check.details, indent=2, default=str))
            lines.append("```")
        lines.append("")

    report_path = REPORTS_DIR / "validation_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


def write_target_and_survey_variables_report(config) -> None:
    admitted_to_hospital_flag = config["target"]["admitted_to_hospital_flag"]
    admitted_via_observation_flag = config["target"]["admitted_via_observation_flag"]

    content = f"""# Target Variable and Survey Design Variables

Generated: {datetime.now(timezone.utc).isoformat()}

## Target Variable

NHAMCS does not provide a single binary "admitted" column. Visit disposition
is recorded as a set of independent 0/1 checkbox items (see technical
documentation, "VISIT DISPOSITION" item group, item numbers 226-241).

The two items relevant to hospital admission are:

- `{admitted_to_hospital_flag}` - "Admit to this hospital" (0 = No, 1 = Yes)
- `{admitted_via_observation_flag}` - "Admit to observation unit, then
  hospitalized" (0 = No, 1 = Yes)

This project defines the prediction target, `{config['target']['derived_target_name']}`,
as:

    hospital_admission = 1 if ({admitted_to_hospital_flag} == 1 or {admitted_via_observation_flag} == 1) else 0

Note: `ADMIT` ("Admitted to:") is a *different* variable describing which
hospital unit (critical care, stepdown, OR, etc.) a patient was admitted to.
It is only populated for visits already flagged as admitted and is not a
usable prediction target on its own.

**Empirical check (this dataset, 16,025 visits):**

| {admitted_to_hospital_flag} | {admitted_via_observation_flag} | Visits |
|---|---|---|
| 0 | 0 | 13,904 |
| 1 | 0 | 1,944 |
| 1 | 1 | 177 |

Every visit with `{admitted_via_observation_flag} == 1` also has
`{admitted_to_hospital_flag} == 1`. In this dataset `{admitted_to_hospital_flag}`
alone already equals the full admitted population (2,121 visits); `{admitted_via_observation_flag}`
adds route-of-admission detail, not additional coverage. The OR-based
derivation above is therefore safe and future-proof (it would still be
correct if a future data release breaks that overlap), but the practical
effect today is equivalent to using `{admitted_to_hospital_flag}` alone.

Deriving the target column itself is a Milestone 5 (Feature Engineering)
task; this milestone only identifies and documents the source variables.

## Survey Design Variables

NHAMCS is a complex, weighted, clustered sample rather than a simple random
sample. The technical documentation (Appendix I.A and Section H) confirms
the survey design with the example:

    svyset [pweight=patwt], psu(cpsum) strata(cstratm)

| Variable | Role | Description |
|---|---|---|
| `{config['survey_design']['weight_variable']}` | Weight | Patient visit weight - required to produce national estimates |
| `{config['survey_design']['strata_variable']}` | Strata | Clustered PSU stratum marker (masked) |
| `{config['survey_design']['cluster_variable']}` | Cluster / PSU | Clustered PSU marker (masked) |
| `{config['survey_design']['facility_weight_variable']}` | Facility weight | ED-level weight; used only for facility-level estimates, not patient-level prediction |

These variables must be preserved through preprocessing for the
survey-aware learning workflow (Milestone 8) and must never be used as
ordinary predictive features in the traditional ML workflow.
"""

    report_path = REPORTS_DIR / "target_and_survey_variables.md"
    report_path.write_text(content, encoding="utf-8")
    logger.info("Wrote %s", report_path)


def main() -> None:
    logger.info("Starting Milestone 1 - Dataset Setup")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config(DEFAULT_CONFIG_PATH)

    try:
        dataframe, metadata = load_dataset(config)
    except FileNotFoundError as error:
        logger.error("Dataset setup aborted: %s", error)
        return

    checks = run_all_validations(dataframe, config)
    for check in checks:
        level = logging.INFO if check.passed else logging.ERROR
        logger.log(level, "[%s] %s: %s", "PASS" if check.passed else "FAIL", check.name, check.message)

    data_dictionary = build_data_dictionary(dataframe, metadata, config)
    dictionary_path = REPORTS_DIR / "data_dictionary.csv"
    data_dictionary.to_csv(dictionary_path, index=False)
    logger.info("Wrote %s (%d variables)", dictionary_path, len(data_dictionary))

    write_dataset_report(dataframe, metadata, config)
    write_dataset_metadata_json(dataframe, metadata, config)
    write_validation_report(checks)
    write_target_and_survey_variables_report(config)

    failed_checks = [check.name for check in checks if not check.passed]
    if failed_checks:
        logger.error("Milestone 1 completed with failed checks: %s", failed_checks)
    else:
        logger.info("Milestone 1 completed successfully. All validation checks passed.")


if __name__ == "__main__":
    main()
