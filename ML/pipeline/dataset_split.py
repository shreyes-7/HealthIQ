"""Splits the raw dataset into train/validation/test row sets, stratified
by the prediction target, before any cleaning or feature engineering runs.

Splitting must happen on the RAW dataframe, not the cleaned/engineered
one: the whole point of Milestone 7 is that the PreprocessingPipeline is
then fit ONLY on the training rows and simply transforms validation/test,
so no statistic learned from validation/test data (imputation medians,
encoder categories, scaler mean/std) ever leaks into the training
artifacts.
"""

import pandas as pd
from sklearn.model_selection import train_test_split

TRAIN_FRACTION = 0.70
VALIDATION_FRACTION = 0.15
TEST_FRACTION = 0.15
RANDOM_STATE = 42


def compute_raw_target_for_stratification(dataframe: pd.DataFrame) -> pd.Series:
    """Mirrors ML.feature_engineering.target.derive_target's definition,
    but operates on the RAW (pre-cleaning) ADMITHOS/OBSHOS columns, which
    are still 0.0/1.0 floats rather than "No"/"Yes" categories."""
    return ((dataframe["ADMITHOS"] == 1) | (dataframe["OBSHOS"] == 1)).astype(int)


def stratified_train_validation_test_split(dataframe: pd.DataFrame) -> dict:
    assert abs(TRAIN_FRACTION + VALIDATION_FRACTION + TEST_FRACTION - 1.0) < 1e-9

    target_for_stratification = compute_raw_target_for_stratification(dataframe)

    train_val_df, test_df = train_test_split(
        dataframe,
        test_size=TEST_FRACTION,
        stratify=target_for_stratification,
        random_state=RANDOM_STATE,
    )

    validation_fraction_of_train_val = VALIDATION_FRACTION / (TRAIN_FRACTION + VALIDATION_FRACTION)
    train_df, validation_df = train_test_split(
        train_val_df,
        test_size=validation_fraction_of_train_val,
        stratify=target_for_stratification.loc[train_val_df.index],
        random_state=RANDOM_STATE,
    )

    return {
        "train": train_df.reset_index(drop=True),
        "validation": validation_df.reset_index(drop=True),
        "test": test_df.reset_index(drop=True),
    }
