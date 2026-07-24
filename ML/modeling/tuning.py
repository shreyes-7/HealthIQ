"""Hyperparameter tuning via randomized search (PROJECT_CONTEXT.md Section 40:
balance performance, generalization, training/inference time, complexity).

Uses a 3-fold search CV to keep the search itself tractable across 7 model
families; once the best hyperparameters are found, the resulting model is
re-evaluated with proper 5-fold cross-validation in Milestone 5
(ML/modeling/cross_validation.py). ROC-AUC is the search objective because
it is threshold-independent and comparable across model families; the full
metric suite (including PR-AUC, which matters more under the ~13% positive
rate) is computed afterward during evaluation, not used to pick
hyperparameters, to keep the two concerns separate.
"""

from sklearn.model_selection import RandomizedSearchCV

SEARCH_ITERATIONS = 15
SEARCH_CV_FOLDS = 3
SCORING_METRIC = "roc_auc"
RANDOM_STATE = 42


def tune_model(estimator, param_distributions: dict, features, target, n_iter: int = SEARCH_ITERATIONS) -> dict:
    search = RandomizedSearchCV(
        estimator=estimator,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=SEARCH_CV_FOLDS,
        scoring=SCORING_METRIC,
        random_state=RANDOM_STATE,
        refit=True,
    )
    search.fit(features, target)

    return {
        "best_estimator": search.best_estimator_,
        "best_params": search.best_params_,
        "best_search_score": float(search.best_score_),
        "scoring_metric": SCORING_METRIC,
        "search_cv_folds": SEARCH_CV_FOLDS,
        "search_iterations": n_iter,
    }
