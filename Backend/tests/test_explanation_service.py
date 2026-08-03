import pytest

from Backend.app.services.explanation_service import ExplanationRuntime, ModelCompatibilityError


@pytest.fixture(scope="module")
def runtime() -> ExplanationRuntime:
    return ExplanationRuntime()


def test_runtime_loads_model_metadata(runtime):
    assert runtime.model_name == "lightgbm"
    assert runtime.model_version == "1.0.0"


def test_explain_raw_patient_returns_expected_keys(runtime, raw_patient_record):
    result = runtime.explain_raw_patient(raw_patient_record)

    assert set(result.keys()) == {
        "predicted_probability",
        "base_rate_probability",
        "predicted_admission",
        "features_that_increased_risk",
        "features_that_decreased_risk",
    }
    assert 0.0 <= result["predicted_probability"] <= 1.0


def test_global_explanation_is_precomputed_not_recomputed(runtime):
    result = runtime.global_explanation(top_n=5)

    assert len(result["top_features"]) == 5
    assert result["computed_on"] == "validation_split"


def test_compatibility_check_rejects_mismatched_feature_names(monkeypatch):
    from ML.explainability import service as explanation_service_module

    original_init = explanation_service_module.ExplanationService.__init__

    def patched_init(self):
        original_init(self)
        self.feature_names = ["not", "the", "real", "features"]

    monkeypatch.setattr(explanation_service_module.ExplanationService, "__init__", patched_init)

    with pytest.raises(ModelCompatibilityError):
        ExplanationRuntime()
