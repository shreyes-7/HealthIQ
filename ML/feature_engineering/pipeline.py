"""Orchestrates Milestone 4 (Feature Engineering) with a fit/transform
contract, mirroring ML/cleaning/pipeline.py:

1. Derive the prediction target from ADMITHOS/OBSHOS.
2. Exclude leakage variables (disposition block, post-admission hospital
   course, facility-level questionnaire items), identifiers, survey
   variables (preserved separately, not as model features), and one
   sparse/redundant variable (AGEDAYS).
3. Remove redundant variables (near-duplicate RFV codes, near-zero-
   variance categorical columns).
4. Encode remaining categorical variables (one-hot / frequency, tiered by
   cardinality).
5. Scale continuous numerical variables (z-score).
6. Reassemble: target + engineered features + untouched survey variables
   + identifiers (kept alongside for traceability, not as model inputs).

Most of this is stateless (the excluded-column sets and the RFV drop are
fixed lists), but three things are genuinely LEARNED from the data and
must be reused rather than recomputed at transform time: which columns
were near-zero-variance, and the fitted CategoricalEncoder/NumericalScaler
themselves. These are captured in `fitted_state` by fit_engineer_features()
and consumed by transform_engineer_features().
"""

import pandas as pd

from ML.cleaning.transformation_log import TransformationLog
from ML.cleaning.variable_roles import CONTINUOUS_NUMERICAL_VARIABLES, IDENTIFIER_VARIABLES, SURVEY_VARIABLES
from ML.feature_engineering.derived_features import (
    DERIVED_CONTINUOUS_COLUMNS,
    add_derived_clinical_features,
)
from ML.feature_engineering.encoding import CategoricalEncoder
from ML.feature_engineering.leakage_exclusion import get_excluded_leakage_columns
from ML.feature_engineering.redundancy import remove_near_zero_variance_categorical, remove_redundant_rfv_codes
from ML.feature_engineering.scaling import NumericalScaler
from ML.feature_engineering.target import derive_target

# Legitimate pre-decision variable, but 97%+ missing outside the infant
# subgroup (codebook: -7 = Not applicable for age >= 1 year) and largely
# redundant with AGE for the general population.
SPARSE_REDUNDANT_VARIABLES = {"AGEDAYS"}


def _get_excluded_columns(dataframe: pd.DataFrame) -> list[str]:
    excluded_columns = (
        get_excluded_leakage_columns() | IDENTIFIER_VARIABLES | SURVEY_VARIABLES | SPARSE_REDUNDANT_VARIABLES
    )
    return sorted(column for column in excluded_columns if column in dataframe.columns)


def _preserved_columns(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    survey_columns = [column for column in SURVEY_VARIABLES if column in dataframe.columns]
    identifier_columns = [column for column in IDENTIFIER_VARIABLES if column in dataframe.columns]
    return dataframe[survey_columns], dataframe[identifier_columns]


def fit_engineer_features(dataframe: pd.DataFrame) -> dict:
    log = TransformationLog()
    dataframe = add_derived_clinical_features(dataframe)
    log.record(
        "derive_clinical_features", "*", "added_derived_clinical_features",
        columns=DERIVED_CONTINUOUS_COLUMNS + ["FEVER_FLAG", "TACHYCARDIC_FLAG", "HYPOTENSIVE_FLAG", "AGE_GROUP"],
    )
    target = derive_target(dataframe)

    excluded_columns = _get_excluded_columns(dataframe)
    log.record(
        "exclude_columns",
        "*",
        "excluded_leakage_identifier_survey_and_sparse_columns",
        count=len(excluded_columns),
        columns=excluded_columns,
    )

    candidate_features = dataframe.drop(columns=excluded_columns)
    candidate_features = remove_redundant_rfv_codes(candidate_features, log)

    continuous_columns = [
        column
        for column in list(CONTINUOUS_NUMERICAL_VARIABLES) + DERIVED_CONTINUOUS_COLUMNS
        if column in candidate_features.columns
    ]
    categorical_columns = [column for column in candidate_features.columns if column not in continuous_columns]

    candidate_features = remove_near_zero_variance_categorical(candidate_features, categorical_columns, log)
    nzv_entry = next(
        (e for e in log.entries_for_step("remove_redundant_variables") if e["action"] == "dropped_near_zero_variance_columns"),
        None,
    )
    near_zero_variance_columns_dropped = nzv_entry["columns"] if nzv_entry else []
    categorical_columns = [column for column in categorical_columns if column in candidate_features.columns]

    encoder = CategoricalEncoder().fit(candidate_features, categorical_columns)
    scaler = NumericalScaler().fit(candidate_features, continuous_columns)

    features = pd.concat(
        [scaler.transform(candidate_features), encoder.transform(candidate_features)], axis=1
    )
    survey, identifiers = _preserved_columns(dataframe)

    log.record(
        "final_feature_set",
        "*",
        "built_final_feature_matrix",
        feature_count=int(features.shape[1]),
        continuous_source_count=len(continuous_columns),
        categorical_source_count=len(categorical_columns),
    )

    fitted_state = {
        "excluded_columns": excluded_columns,
        "near_zero_variance_columns_dropped": near_zero_variance_columns_dropped,
        "continuous_columns": continuous_columns,
        "categorical_columns": categorical_columns,
        "encoder": encoder,
        "scaler": scaler,
    }

    return {
        "target": target,
        "features": features,
        "survey": survey,
        "identifiers": identifiers,
        "log": log,
        "fitted_state": fitted_state,
    }


def transform_engineer_features(dataframe: pd.DataFrame, fitted_state: dict) -> dict:
    """Applies the SAME feature engineering decisions learned by
    fit_engineer_features() to a new dataset."""
    log = TransformationLog()
    dataframe = add_derived_clinical_features(dataframe)
    target = derive_target(dataframe)

    excluded_columns = [column for column in fitted_state["excluded_columns"] if column in dataframe.columns]
    candidate_features = dataframe.drop(columns=excluded_columns)
    candidate_features = remove_redundant_rfv_codes(candidate_features, log)

    nzv_columns = [
        column for column in fitted_state["near_zero_variance_columns_dropped"] if column in candidate_features.columns
    ]
    candidate_features = candidate_features.drop(columns=nzv_columns)
    log.record(
        "reuse_fitted_column_drops", "*", "dropped_near_zero_variance_columns_identified_during_fit", columns=nzv_columns
    )

    encoder = fitted_state["encoder"]
    scaler = fitted_state["scaler"]
    features = pd.concat(
        [scaler.transform(candidate_features), encoder.transform(candidate_features)], axis=1
    )
    survey, identifiers = _preserved_columns(dataframe)

    return {"target": target, "features": features, "survey": survey, "identifiers": identifiers, "log": log}
