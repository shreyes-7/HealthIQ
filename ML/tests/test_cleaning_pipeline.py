"""Integration tests for the cleaning fit/transform contract
(ML/cleaning/pipeline.py), using a small real raw-data slice."""

from ML.cleaning.pipeline import fit_clean_dataset, transform_clean_dataset


def test_fit_clean_dataset_produces_fitted_state_for_reuse(small_raw_sample):
    cleaned, log, fitted_state = fit_clean_dataset(small_raw_sample)

    assert set(fitted_state.keys()) >= {
        "duplicate_columns_dropped", "constant_columns_dropped", "boolean_columns",
        "categorical_columns", "continuous_medians",
    }
    assert cleaned.shape[0] == small_raw_sample.shape[0]
    assert len(log.entries) > 0


def test_transform_reuses_fitted_state_without_recomputing(small_raw_sample):
    fit_half = small_raw_sample.iloc[:200].reset_index(drop=True)
    transform_half = small_raw_sample.iloc[200:].reset_index(drop=True)

    _cleaned_fit, _log, fitted_state = fit_clean_dataset(fit_half)
    cleaned_transform, _transform_log = transform_clean_dataset(transform_half, fitted_state)

    # transform_clean_dataset must drop exactly the columns identified during fit.
    for column in fitted_state["duplicate_columns_dropped"] + fitted_state["constant_columns_dropped"]:
        assert column not in cleaned_transform.columns


def test_survey_variables_are_byte_identical_after_cleaning(small_raw_sample):
    cleaned, _log, _fitted_state = fit_clean_dataset(small_raw_sample)

    original_sorted = small_raw_sample["PATWT"].sort_values().reset_index(drop=True)
    cleaned_sorted = cleaned["PATWT"].sort_values().reset_index(drop=True)
    assert original_sorted.equals(cleaned_sorted)
