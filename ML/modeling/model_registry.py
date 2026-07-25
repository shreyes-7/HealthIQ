"""Registry of Sprint 2's candidate models (PROJECT_CONTEXT.md Section 39).

Each entry provides an unfitted-estimator factory and a hyperparameter
search space for RandomizedSearchCV, so the training/tuning code in
tuning.py stays generic across model families instead of special-casing
each one.

Class imbalance (13.24% positive) is treated as a tunable hyperparameter
per model (`class_weight` / `scale_pos_weight` / `auto_class_weights`)
rather than a fixed assumption, so the search empirically decides whether
balancing helps for each model family.
"""

from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

RANDOM_STATE = 42


def _logistic_regression():
    # liblinear converges in ~2.6s on this 866-feature matrix (17 iterations);
    # saga was benchmarked at ~155s and still failed to converge within
    # max_iter=1000. liblinear supports both L1 and L2 (no elasticnet, not
    # needed here) and is the right choice for this binary-classification,
    # tens-of-thousands-of-rows scale.
    return LogisticRegression(solver="liblinear", max_iter=1000, random_state=RANDOM_STATE)


def _decision_tree():
    return DecisionTreeClassifier(random_state=RANDOM_STATE)


def _random_forest():
    return RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)


def _gradient_boosting():
    return GradientBoostingClassifier(random_state=RANDOM_STATE)


def _xgboost():
    return XGBClassifier(random_state=RANDOM_STATE, eval_metric="logloss", n_jobs=-1)


def _lightgbm():
    # subsample_freq must be > 0 for `subsample` to have any effect at all.
    return LGBMClassifier(random_state=RANDOM_STATE, n_jobs=-1, verbosity=-1, subsample_freq=1)


def _catboost():
    return CatBoostClassifier(random_state=RANDOM_STATE, verbose=0)


MODEL_REGISTRY = {
    "logistic_regression": {
        "estimator_factory": _logistic_regression,
        "param_distributions": {
            "C": [0.001, 0.01, 0.1, 1.0, 10.0, 100.0],
            "penalty": ["l1", "l2"],
            "class_weight": [None, "balanced"],
        },
        "interpretability": "high",
    },
    "decision_tree": {
        "estimator_factory": _decision_tree,
        "param_distributions": {
            "max_depth": [3, 5, 8, 12, 20, None],
            "min_samples_split": [2, 5, 10, 20],
            "min_samples_leaf": [1, 2, 5, 10],
            "class_weight": [None, "balanced"],
        },
        "interpretability": "high",
    },
    "random_forest": {
        "estimator_factory": _random_forest,
        "param_distributions": {
            "n_estimators": [100, 200, 400, 600],
            "max_depth": [5, 8, 12, 20, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2", 0.3],
            "class_weight": [None, "balanced", "balanced_subsample"],
        },
        "interpretability": "medium",
    },
    "gradient_boosting": {
        "estimator_factory": _gradient_boosting,
        "param_distributions": {
            "n_estimators": [100, 200, 300],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "max_depth": [2, 3, 4, 5],
            "subsample": [0.7, 0.85, 1.0],
        },
        "interpretability": "medium",
    },
    "xgboost": {
        "estimator_factory": _xgboost,
        "param_distributions": {
            "n_estimators": [100, 200, 400],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "max_depth": [3, 4, 5, 6, 8],
            "subsample": [0.7, 0.85, 1.0],
            "colsample_bytree": [0.6, 0.8, 1.0],
            "scale_pos_weight": [1, 3, 6.56, 10],
        },
        "interpretability": "medium",
    },
    "lightgbm": {
        "estimator_factory": _lightgbm,
        "param_distributions": {
            "n_estimators": [100, 200, 400],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "num_leaves": [15, 31, 63, 127],
            "max_depth": [-1, 5, 8, 12],
            "subsample": [0.7, 0.85, 1.0],
            "class_weight": [None, "balanced"],
        },
        "interpretability": "medium",
    },
    "catboost": {
        "estimator_factory": _catboost,
        "param_distributions": {
            "iterations": [200, 400, 600],
            "learning_rate": [0.01, 0.05, 0.1, 0.2],
            "depth": [4, 6, 8, 10],
            "l2_leaf_reg": [1, 3, 5, 10],
            "auto_class_weights": [None, "Balanced"],
        },
        "interpretability": "medium",
    },
}
