# Explainability Readiness Report

Generated: 2026-07-25T07:53:44.110521+00:00

## Overall: READY

Selected model: `lightgbm` (version 1.0.0, 866 features)

No model was retrained. All artifacts below were loaded, not regenerated.

## Checks

- [PASS] `load_preprocessing_pipeline`
- [PASS] `load_best_model` — LGBMClassifier
- [PASS] `load_feature_metadata` — 866 features (metadata claims 866)
- [PASS] `load_train_dataset` — (11217, 873)
- [PASS] `load_validation_dataset` — (2404, 873)
- [PASS] `load_test_dataset` — (2404, 873)
- [PASS] `feature_ordering_matches_train_split`
- [PASS] `feature_ordering_matches_model_booster`
- [PASS] `preprocessing_output_matches_model_features`
- [PASS] `model_predicts_on_pipeline_output`

## Notes

- `feature_ordering_matches_model_booster` and `model_predicts_on_pipeline_output` are the checks that matter most for SHAP correctness: SHAP values are positional (one value per feature column, in the order the model was trained on), so any ordering drift between the pipeline's output and the model's expectation would silently misattribute every explanation.