"""Unit tests for pure SHAP utility functions (ML/explainability/shap_utils.py).

Sprint 3's Milestone 7 (Explanation Validation) already provides thorough
executable verification of SHAP-specific correctness (reconstruction,
determinism, ordering) against the real model -- these tests cover the
small pure functions other modules build on, as fast regression guards.
"""

import numpy as np
import pandas as pd

from ML.explainability.cohort import reconstruct_categorical_from_onehot
from ML.explainability.shap_utils import mean_absolute_shap_by_feature, sigmoid, source_variable_name


def test_sigmoid_at_zero_is_one_half():
    assert abs(sigmoid(0.0) - 0.5) < 1e-9


def test_sigmoid_matches_known_values():
    # sigmoid(-8.3) should be a very small probability, sigmoid(8.3) very large.
    assert sigmoid(-8.3) < 0.01
    assert sigmoid(8.3) > 0.99


def test_source_variable_name_strips_one_hot_suffix():
    assert source_variable_name("SEX__2") == "SEX"
    assert source_variable_name("DIAG1__frequency") == "DIAG1"
    assert source_variable_name("AGE") == "AGE"  # no suffix -- returned as-is


def test_mean_absolute_shap_by_feature_ranks_correctly():
    shap_values = np.array([[1.0, -0.5], [2.0, 0.5], [-3.0, 0.0]])
    ranking = mean_absolute_shap_by_feature(shap_values, ["A", "B"])
    assert ranking.index[0] == "A"  # mean |shap| = 2.0 > B's 0.333
    assert ranking.iloc[0] > ranking.iloc[1]


def test_reconstruct_categorical_from_onehot_uses_reference_when_no_dummy_set():
    features = pd.DataFrame({"SEX__2": [0, 1, 0]})
    encoder_metadata = {"SEX": {"reference_category": "1", "encoded_categories": ["2"]}}
    result = reconstruct_categorical_from_onehot(features, "SEX", encoder_metadata)
    assert list(result) == ["1", "2", "1"]
