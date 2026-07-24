"""Integration tests for the end-to-end reusable pipeline
(ML/pipeline/preprocessing_pipeline.py), using a small real raw-data
slice. This is the property the whole Milestone 9/11 effort exists to
guarantee: fit once, transform new data later, with identical schema and
without recomputing learned statistics."""

import pandas as pd
import pytest

from ML.pipeline.preprocessing_pipeline import PreprocessingPipeline


def test_transform_before_fit_raises():
    pipeline = PreprocessingPipeline()
    with pytest.raises(RuntimeError):
        pipeline.transform(pd.DataFrame())


def test_fit_transform_and_transform_produce_identical_feature_schema(small_raw_sample):
    fit_half = small_raw_sample.iloc[:200].reset_index(drop=True)
    transform_half = small_raw_sample.iloc[200:].reset_index(drop=True)

    pipeline = PreprocessingPipeline()
    fit_result = pipeline.fit_transform(fit_half)
    transform_result = pipeline.transform(transform_half)

    assert list(fit_result["features"].columns) == list(transform_result["features"].columns)


def test_survey_variables_pass_through_untouched(small_raw_sample):
    pipeline = PreprocessingPipeline()
    result = pipeline.fit_transform(small_raw_sample)

    assert set(result["survey"].columns) == {"PATWT", "EDWT", "CSTRATM", "CPSUM"}
    original_sorted = small_raw_sample["PATWT"].sort_values().reset_index(drop=True)
    result_sorted = result["survey"]["PATWT"].sort_values().reset_index(drop=True)
    assert original_sorted.equals(result_sorted)


def test_no_missing_values_in_feature_matrix(small_raw_sample):
    pipeline = PreprocessingPipeline()
    result = pipeline.fit_transform(small_raw_sample)

    assert result["features"].isna().sum().sum() == 0


def test_save_and_load_round_trip(tmp_path, small_raw_sample):
    pipeline = PreprocessingPipeline()
    fit_result = pipeline.fit_transform(small_raw_sample)

    pipeline.save(tmp_path)
    reloaded = PreprocessingPipeline.load(tmp_path)

    assert reloaded.is_fitted
    transform_result = reloaded.transform(small_raw_sample)
    assert list(transform_result["features"].columns) == list(fit_result["features"].columns)
