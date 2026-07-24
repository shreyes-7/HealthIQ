"""Builds a data dictionary describing every variable in the raw dataset."""

from typing import Any

import pandas as pd


def _classify_role(variable_name: str, config: dict) -> str:
    survey_variables = {
        config["survey_design"]["weight_variable"],
        config["survey_design"]["strata_variable"],
        config["survey_design"]["cluster_variable"],
        config["survey_design"]["facility_weight_variable"],
    }
    target_variables = {
        config["target"]["admitted_to_hospital_flag"],
        config["target"]["admitted_via_observation_flag"],
    }

    if variable_name in target_variables:
        return "target"
    if variable_name in survey_variables:
        return "survey_design"
    return "general"


def build_data_dictionary(dataframe: pd.DataFrame, metadata: Any, config: dict) -> pd.DataFrame:
    """Build one row per variable describing its label, type, and completeness."""
    row_count = len(dataframe)
    labels = metadata.column_names_to_labels

    records = []
    for column_name in dataframe.columns:
        missing_count = int(dataframe[column_name].isna().sum())
        records.append(
            {
                "variable_name": column_name,
                "label": labels.get(column_name, ""),
                "pandas_dtype": str(dataframe[column_name].dtype),
                "non_null_count": row_count - missing_count,
                "missing_count": missing_count,
                "missing_percentage": round(missing_count / row_count * 100, 2),
                "n_unique": int(dataframe[column_name].nunique(dropna=True)),
                "role": _classify_role(column_name, config),
            }
        )

    return pd.DataFrame.from_records(records)
