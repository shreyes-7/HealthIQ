"""Validates the loaded NHAMCS dataset. Read-only: never modifies the dataframe."""

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class ValidationCheck:
    name: str
    passed: bool
    message: str
    details: Optional[dict] = None


def validate_expected_shape(dataframe: pd.DataFrame, config: dict) -> ValidationCheck:
    expected_rows = config["dataset"]["expected_row_count"]
    expected_columns = config["dataset"]["expected_column_count"]
    actual_rows, actual_columns = dataframe.shape

    passed = actual_rows == expected_rows and actual_columns == expected_columns
    message = (
        f"Expected {expected_rows} rows x {expected_columns} columns, "
        f"found {actual_rows} rows x {actual_columns} columns."
    )
    return ValidationCheck("expected_shape", passed, message)


def validate_required_columns_present(
    dataframe: pd.DataFrame, required_columns: list[str], check_name: str
) -> ValidationCheck:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    passed = len(missing_columns) == 0
    message = (
        "All required columns are present."
        if passed
        else f"Missing required columns: {missing_columns}"
    )
    return ValidationCheck(check_name, passed, message, details={"missing_columns": missing_columns})


def validate_target_variables_present(dataframe: pd.DataFrame, config: dict) -> ValidationCheck:
    target_columns = [
        config["target"]["admitted_to_hospital_flag"],
        config["target"]["admitted_via_observation_flag"],
    ]
    return validate_required_columns_present(dataframe, target_columns, "target_variables_present")


def validate_survey_variables_present(dataframe: pd.DataFrame, config: dict) -> ValidationCheck:
    survey_columns = [
        config["survey_design"]["weight_variable"],
        config["survey_design"]["strata_variable"],
        config["survey_design"]["cluster_variable"],
        config["survey_design"]["facility_weight_variable"],
    ]
    return validate_required_columns_present(dataframe, survey_columns, "survey_variables_present")


def check_duplicate_rows(dataframe: pd.DataFrame) -> ValidationCheck:
    duplicate_count = int(dataframe.duplicated().sum())
    message = f"{duplicate_count} fully duplicate row(s) found (informational; no rows removed)."
    return ValidationCheck(
        "duplicate_rows", passed=True, message=message, details={"duplicate_count": duplicate_count}
    )


def summarize_missing_values(dataframe: pd.DataFrame, top_n: int = 15) -> ValidationCheck:
    missing_counts = dataframe.isna().sum()
    missing_percentage = (missing_counts / len(dataframe) * 100).round(2)
    top_missing = missing_percentage.sort_values(ascending=False).head(top_n)
    fully_missing_columns = missing_percentage[missing_percentage == 100.0].index.tolist()

    message = (
        f"{len(fully_missing_columns)} column(s) are 100% missing. "
        f"Top {top_n} columns by missing percentage recorded in details."
    )
    return ValidationCheck(
        "missing_values_summary",
        passed=True,
        message=message,
        details={
            "fully_missing_columns": fully_missing_columns,
            "top_missing_percentage": top_missing.to_dict(),
        },
    )


def summarize_target_distribution(dataframe: pd.DataFrame, config: dict) -> ValidationCheck:
    admitted_to_hospital_flag = config["target"]["admitted_to_hospital_flag"]
    admitted_via_observation_flag = config["target"]["admitted_via_observation_flag"]

    admitted_to_hospital_counts = dataframe[admitted_to_hospital_flag].value_counts(dropna=False).to_dict()
    admitted_via_observation_counts = dataframe[admitted_via_observation_flag].value_counts(dropna=False).to_dict()

    derived_target = (
        (dataframe[admitted_to_hospital_flag] == 1) | (dataframe[admitted_via_observation_flag] == 1)
    ).astype(int)
    derived_target_counts = derived_target.value_counts().to_dict()

    return ValidationCheck(
        "target_distribution",
        passed=True,
        message="Target variable value distributions recorded in details.",
        details={
            admitted_to_hospital_flag: admitted_to_hospital_counts,
            admitted_via_observation_flag: admitted_via_observation_counts,
            "derived_hospital_admission": derived_target_counts,
        },
    )


def run_all_validations(dataframe: pd.DataFrame, config: dict) -> list[ValidationCheck]:
    """Run every validation check and return the full list of results."""
    return [
        validate_expected_shape(dataframe, config),
        validate_target_variables_present(dataframe, config),
        validate_survey_variables_present(dataframe, config),
        check_duplicate_rows(dataframe),
        summarize_missing_values(dataframe),
        summarize_target_distribution(dataframe, config),
    ]
