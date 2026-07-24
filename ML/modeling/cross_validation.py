"""Stratified k-fold cross-validation, run identically for every candidate
model so results are directly comparable (PROJECT_CONTEXT.md Section 41).
"""

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedKFold

from ML.modeling.metrics import compute_classification_metrics

DEFAULT_N_FOLDS = 5
RANDOM_STATE = 42


def cross_validate_model(
    model, features: pd.DataFrame, target: pd.Series, n_folds: int = DEFAULT_N_FOLDS
) -> dict:
    """Fits a fresh clone of `model` on each fold's training portion and
    scores it on that fold's held-out portion. Returns per-fold metrics
    plus the mean/std across folds."""
    stratified_kfold = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=RANDOM_STATE)

    fold_metrics = []
    for train_index, validation_index in stratified_kfold.split(features, target):
        fold_model = clone(model)
        fold_model.fit(features.iloc[train_index], target.iloc[train_index])

        fold_probabilities = fold_model.predict_proba(features.iloc[validation_index])[:, 1]
        fold_metrics.append(compute_classification_metrics(target.iloc[validation_index], fold_probabilities))

    aggregated = {}
    for metric_name in fold_metrics[0]:
        if metric_name in ("confusion_matrix", "threshold"):
            continue
        values = [fold[metric_name] for fold in fold_metrics]
        aggregated[metric_name] = {"mean": float(np.mean(values)), "std": float(np.std(values))}

    return {"n_folds": n_folds, "fold_metrics": fold_metrics, "aggregated": aggregated}
