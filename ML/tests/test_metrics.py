"""Unit tests for ML/modeling/metrics.py."""

import numpy as np

from ML.modeling.metrics import compute_calibration_curve, compute_classification_metrics, compute_pr_curve, compute_roc_curve


def test_perfect_predictions_score_maximally():
    y_true = [0, 0, 1, 1]
    y_proba = [0.01, 0.02, 0.98, 0.99]
    metrics = compute_classification_metrics(y_true, y_proba)

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["specificity"] == 1.0
    assert metrics["roc_auc"] == 1.0


def test_confusion_matrix_counts_are_correct():
    y_true = [0, 0, 1, 1]
    y_proba = [0.1, 0.6, 0.4, 0.9]  # one false positive, one false negative
    metrics = compute_classification_metrics(y_true, y_proba)

    matrix = metrics["confusion_matrix"]
    assert matrix["true_negative"] == 1
    assert matrix["false_positive"] == 1
    assert matrix["false_negative"] == 1
    assert matrix["true_positive"] == 1


def test_custom_threshold_changes_predictions():
    y_true = [0, 1]
    y_proba = [0.3, 0.3]

    low_threshold_metrics = compute_classification_metrics(y_true, y_proba, threshold=0.2)
    high_threshold_metrics = compute_classification_metrics(y_true, y_proba, threshold=0.8)

    # At threshold 0.2 both are predicted positive; at 0.8 both are predicted negative.
    assert low_threshold_metrics["confusion_matrix"]["true_positive"] == 1
    assert high_threshold_metrics["confusion_matrix"]["true_positive"] == 0


def test_sensitivity_equals_recall():
    y_true = np.random.RandomState(0).randint(0, 2, size=50)
    y_proba = np.random.RandomState(1).uniform(size=50)
    metrics = compute_classification_metrics(y_true, y_proba)

    assert metrics["sensitivity"] == metrics["recall"]


def test_roc_curve_has_matching_length_arrays():
    y_true = [0, 0, 1, 1]
    y_proba = [0.1, 0.4, 0.6, 0.9]
    curve = compute_roc_curve(y_true, y_proba)

    assert len(curve["false_positive_rate"]) == len(curve["true_positive_rate"]) == len(curve["thresholds"])


def test_pr_curve_has_matching_length_arrays():
    y_true = [0, 0, 1, 1]
    y_proba = [0.1, 0.4, 0.6, 0.9]
    curve = compute_pr_curve(y_true, y_proba)

    assert len(curve["precision"]) == len(curve["recall"])


def test_calibration_curve_returns_bounded_fractions():
    y_true = np.random.RandomState(0).randint(0, 2, size=200)
    y_proba = np.random.RandomState(1).uniform(size=200)
    curve = compute_calibration_curve(y_true, y_proba, n_bins=5)

    assert all(0.0 <= value <= 1.0 for value in curve["fraction_of_positives"])
