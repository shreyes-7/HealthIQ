"""Sprint 2 Milestone 7: stacking ensemble combining the strongest
individual candidate models (PROJECT_CONTEXT.md Section 39 explicitly
lists "Ensemble Models" alongside the individual algorithms).

Reuses each base model's ALREADY-TUNED hyperparameters from Milestone 4
-- this does not re-run hyperparameter search for the base learners.
sklearn's StackingClassifier internally cross-fits the base estimators to
generate out-of-fold predictions for the meta-learner, then refits each
base estimator on the full training data, so passing already-tuned-but-
unfitted estimators here is correct and leakage-free.
"""

from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from ML.modeling.experiment_log import ExperimentLog
from ML.modeling.model_registry import MODEL_REGISTRY

RANDOM_STATE = 42
STACK_CV_FOLDS = 5
TOP_N_BASE_MODELS = 3

# gradient_boosting and catboost are excluded from stacking candidacy
# despite strong standalone validation performance (ROC-AUC 0.9515 and
# 0.9609): single fits took ~1220s and ~485s respectively in Milestone
# 3-5 (gradient_boosting has no internal parallelism; catboost's search
# space favored many iterations). StackingClassifier's internal 5-fold
# cross-fit plus a final refit multiplies that ~6x per base model, which
# would make either one alone take 48+ minutes. xgboost and lightgbm
# already capture similar boosted-tree signal at a fraction of the
# runtime, so the practical loss from excluding these two is minimal
# relative to the cost.
EXCLUDED_FROM_STACKING = {"gradient_boosting", "catboost"}


def select_top_models(experiment_log: ExperimentLog, top_n: int = TOP_N_BASE_MODELS) -> list[str]:
    eligible_records = [record for record in experiment_log.records if record.model_name not in EXCLUDED_FROM_STACKING]
    ranked = sorted(eligible_records, key=lambda record: record.validation_metrics["roc_auc"], reverse=True)
    return [record.model_name for record in ranked[:top_n]]


def build_stacking_ensemble(experiment_log: ExperimentLog, top_n: int = TOP_N_BASE_MODELS) -> StackingClassifier:
    top_model_names = select_top_models(experiment_log, top_n)

    base_estimators = []
    for model_name in top_model_names:
        record = experiment_log.get(model_name)
        estimator = MODEL_REGISTRY[model_name]["estimator_factory"]().set_params(**record.hyperparameters)
        base_estimators.append((model_name, estimator))

    return StackingClassifier(
        estimators=base_estimators,
        final_estimator=LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        cv=StratifiedKFold(n_splits=STACK_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE),
        n_jobs=1,
    )
