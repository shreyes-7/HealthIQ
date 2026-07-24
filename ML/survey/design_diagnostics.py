"""Survey design diagnostics for the NHAMCS patient-visit weight, strata,
and PSU (cluster) variables.

This module does NOT perform survey-weighted estimation or modeling --
that is explicitly a Phase 2 concern (PROJECT_CONTEXT.md's "Survey-Aware
Machine Learning" research objective, which compares conventional vs
survey-aware model fits). It only verifies that the survey design
variables survived preprocessing intact and reports diagnostics a
survey-aware modeling step will need.
"""

import pandas as pd

WEIGHT_COLUMN = "PATWT"
STRATA_COLUMN = "CSTRATM"
PSU_COLUMN = "CPSUM"
FACILITY_WEIGHT_COLUMN = "EDWT"


def summarize_survey_design(dataframe: pd.DataFrame) -> dict:
    weights = dataframe[WEIGHT_COLUMN]
    weight_mean = weights.mean()
    weight_std = weights.std()
    # Kish's approximate design effect from weight variability alone:
    # deff ~= 1 + CV(weights)^2 (Kish, 1965). A simplified, weight-only
    # proxy -- NOT a full variance-based design effect, which requires an
    # actual outcome and a proper survey-design estimator (Phase 2).
    weight_cv = (weight_std / weight_mean) if weight_mean else float("nan")
    approximate_kish_design_effect = 1 + weight_cv**2

    return {
        "row_count": int(len(dataframe)),
        "unique_strata": int(dataframe[STRATA_COLUMN].nunique()),
        "unique_psus": int(dataframe[PSU_COLUMN].nunique()),
        "weight_sum": float(weights.sum()),
        "weight_mean": float(weight_mean),
        "weight_std": float(weight_std),
        "weight_min": float(weights.min()),
        "weight_max": float(weights.max()),
        "weight_coefficient_of_variation": float(weight_cv),
        "approximate_kish_design_effect": float(approximate_kish_design_effect),
        "facility_weight_non_null_count": int(dataframe[FACILITY_WEIGHT_COLUMN].notna().sum()),
    }


def psu_overlap_across_splits(splits: dict[str, pd.DataFrame]) -> dict:
    """Reports how many PSUs (CPSUM values) appear in more than one
    split. A stratified-by-target row split (Milestone 7) does not
    preserve PSU clustering, so the same PSU (loosely, a hospital-level
    sampling unit) can and does appear in both train and held-out splits.
    This is fine for the traditional ML workflow's evaluation, but is a
    methodological caveat for rigorous survey-weighted variance estimation,
    which typically assumes independence between the PSUs used to fit vs
    evaluate a design-based estimate."""
    psu_sets = {name: set(frame[PSU_COLUMN].unique()) for name, frame in splits.items()}
    split_names = list(psu_sets.keys())

    overlaps = {}
    for i, name_a in enumerate(split_names):
        for name_b in split_names[i + 1 :]:
            shared = psu_sets[name_a] & psu_sets[name_b]
            overlaps[f"{name_a}_and_{name_b}"] = {
                "shared_psu_count": len(shared),
                f"{name_a}_psu_count": len(psu_sets[name_a]),
                f"{name_b}_psu_count": len(psu_sets[name_b]),
            }

    return overlaps
