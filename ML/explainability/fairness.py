"""Survey-Aware Deep Dive, Part 3: fairness audit across a demographic
dimension, comparing the survey-weighted and unweighted models.

This is the piece PROJECT_CONTEXT.md §44 explicitly names as one of the
things survey-aware learning should be evaluated on ("Fairness") that had
never been assessed at all before this. Uses `RACERETH` (race/ethnicity,
combined and NHAMCS-imputed so there is no missing category to handle
separately) as the protected-attribute dimension: 1=Non-Hispanic White,
2=Non-Hispanic Black, 3=Hispanic, 4=Non-Hispanic Other (confirmed against
the NCHS codebook, not assumed).

Standard fairness-audit metrics, computed per group at the same 0.5
decision threshold used everywhere else in this project:
- Selection rate: P(predicted admit) -- demographic parity is about
  whether this is equal across groups.
- True Positive Rate (sensitivity/recall): P(predicted admit | actually
  admitted) -- equal opportunity is about whether this is equal across
  groups.
- False Positive Rate: P(predicted admit | actually not admitted).
- ROC-AUC per group: whether the model discriminates equally well within
  each group, independent of any fixed threshold.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

FAIRNESS_THRESHOLD = 0.5


def compute_group_fairness_metrics(probabilities: np.ndarray, target: pd.Series, group_labels: pd.Series) -> dict:
    predictions = (probabilities >= FAIRNESS_THRESHOLD).astype(int)
    target_values = target.values
    predictions = np.asarray(predictions)

    results = {}
    for group_value in sorted(group_labels.dropna().unique(), key=str):
        group_mask = (group_labels == group_value).values
        group_size = int(group_mask.sum())
        if group_size == 0:
            continue

        group_target = target_values[group_mask]
        group_predictions = predictions[group_mask]
        group_probabilities = probabilities[group_mask]

        actually_admitted = group_target == 1
        actually_not_admitted = group_target == 0

        true_positive_rate = (
            float((group_predictions[actually_admitted] == 1).mean()) if actually_admitted.any() else None
        )
        false_positive_rate = (
            float((group_predictions[actually_not_admitted] == 1).mean()) if actually_not_admitted.any() else None
        )
        group_auc = (
            float(roc_auc_score(group_target, group_probabilities))
            if len(np.unique(group_target)) > 1 else None
        )

        results[str(group_value)] = {
            "n": group_size,
            "actual_admission_rate": float(actually_admitted.mean()),
            "selection_rate": float(group_predictions.mean()),
            "true_positive_rate": true_positive_rate,
            "false_positive_rate": false_positive_rate,
            "roc_auc": group_auc,
        }

    return results


def summarize_disparity(group_metrics: dict) -> dict:
    """Standard fairness-audit summary: the max-min gap across groups for
    each metric. Larger gaps indicate the model treats groups more
    differently."""
    summary = {}
    for metric in ("selection_rate", "true_positive_rate", "false_positive_rate", "roc_auc"):
        values = [group[metric] for group in group_metrics.values() if group[metric] is not None]
        if not values:
            continue
        summary[metric] = {
            "min": min(values),
            "max": max(values),
            "gap": max(values) - min(values),
        }
    return summary
