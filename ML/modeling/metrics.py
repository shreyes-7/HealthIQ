"""Standardized binary-classification evaluation metrics.

Every model in Sprint 2 is scored with the same function, so comparisons
across models are apples-to-apples (PROJECT_CONTEXT.md Section 41: Model
Evaluation should extend beyond simple accuracy).
"""

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

CLASSIFICATION_THRESHOLD = 0.5


def compute_classification_metrics(y_true, y_proba, threshold: float = CLASSIFICATION_THRESHOLD) -> dict:
    """Computes the full evaluation suite from true labels and predicted
    probabilities. Predictions are derived from y_proba at a fixed
    threshold so every model is compared at the same operating point."""
    y_pred = (np.asarray(y_proba) >= threshold).astype(int)

    true_negative, false_positive, false_negative, true_positive = confusion_matrix(y_true, y_pred).ravel()
    specificity = true_negative / (true_negative + false_positive) if (true_negative + false_positive) else 0.0
    sensitivity = true_positive / (true_positive + false_negative) if (true_positive + false_negative) else 0.0

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "brier_score": float(brier_score_loss(y_true, y_proba)),
        "confusion_matrix": {
            "true_negative": int(true_negative),
            "false_positive": int(false_positive),
            "false_negative": int(false_negative),
            "true_positive": int(true_positive),
        },
        "threshold": threshold,
    }


def compute_roc_curve(y_true, y_proba) -> dict:
    false_positive_rate, true_positive_rate, thresholds = roc_curve(y_true, y_proba)
    return {
        "false_positive_rate": false_positive_rate.tolist(),
        "true_positive_rate": true_positive_rate.tolist(),
        "thresholds": thresholds.tolist(),
    }


def compute_pr_curve(y_true, y_proba) -> dict:
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
    return {"precision": precision.tolist(), "recall": recall.tolist(), "thresholds": thresholds.tolist()}


def compute_calibration_curve(y_true, y_proba, n_bins: int = 10) -> dict:
    fraction_of_positives, mean_predicted_value = calibration_curve(y_true, y_proba, n_bins=n_bins, strategy="quantile")
    return {"fraction_of_positives": fraction_of_positives.tolist(), "mean_predicted_value": mean_predicted_value.tolist()}
