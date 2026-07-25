"""Survey-Aware Deep Dive, Part 1: weighted vs. unweighted LightGBM.

Sprint 2 Milestone 8's survey-aware comparison used Logistic Regression
only -- the actual production model (LightGBM) was never evaluated in a
survey-aware form at all. This module closes that gap: fits a
survey-weighted LightGBM using the EXACT SAME hyperparameters as the
production model (from `experiment_log.json`), on the SAME training data,
with `sample_weight=PATWT` as the only difference -- isolating the effect
of survey weighting specifically, the same clean experimental design
Sprint 2 used for its Logistic Regression comparison.

The production model already has `class_weight="balanced"` baked into
its tuned hyperparameters (LightGBM's own class-imbalance handling).
That is deliberately kept identical between both variants here --
`sample_weight=PATWT` is the ONLY additional difference, so any change in
behavior is attributable to survey weighting, not to class-imbalance
handling changing too.
"""

import json

import lightgbm
import pandas as pd

from ML.ingestion.config import resolve_repo_path

MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")


def get_production_hyperparameters(model_name: str = "lightgbm") -> dict:
    experiment_log = json.loads((MODELING_REPORTS_DIR / "experiment_log.json").read_text())
    record = next(r for r in experiment_log if r["model_name"] == model_name)
    return dict(record["hyperparameters"])


def fit_survey_weighted_model(features: pd.DataFrame, target: pd.Series, weights: pd.Series, random_state: int = 42):
    hyperparameters = get_production_hyperparameters("lightgbm")
    model = lightgbm.LGBMClassifier(**hyperparameters, random_state=random_state, verbose=-1)
    model.fit(features, target, sample_weight=weights)
    return model
