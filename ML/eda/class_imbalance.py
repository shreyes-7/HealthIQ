"""Class imbalance analysis for the derived prediction target.

The target is computed in-memory for analysis only; it is not written back
to the raw dataset. Deriving and persisting the target column is a
Milestone 5 (Feature Engineering) task.
"""

import pandas as pd


def compute_derived_target(dataframe: pd.DataFrame, config: dict) -> pd.Series:
    admitted_to_hospital_flag = config["target"]["admitted_to_hospital_flag"]
    admitted_via_observation_flag = config["target"]["admitted_via_observation_flag"]

    is_admitted = (
        (dataframe[admitted_to_hospital_flag] == 1) | (dataframe[admitted_via_observation_flag] == 1)
    )
    return is_admitted.astype(int).rename(config["target"]["derived_target_name"])


def analyze_class_imbalance(target: pd.Series) -> dict:
    counts = target.value_counts().sort_index()
    percentages = (counts / len(target) * 100).round(2)

    majority_count = int(counts.max())
    minority_count = int(counts.min())
    imbalance_ratio = round(majority_count / minority_count, 2) if minority_count else None

    return {
        "counts": {str(key): int(value) for key, value in counts.items()},
        "percentages": {str(key): float(value) for key, value in percentages.items()},
        "imbalance_ratio": imbalance_ratio,
    }
