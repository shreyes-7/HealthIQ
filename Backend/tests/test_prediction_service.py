import pytest

from Backend.app.services.explanation_service import ExplanationRuntime
from Backend.app.services.prediction_service import _confidence_score, _risk_category, predict_and_explain


@pytest.fixture(scope="module")
def runtime() -> ExplanationRuntime:
    return ExplanationRuntime()


@pytest.mark.parametrize(
    "probability,expected",
    [(0.9, "high"), (0.75, "high"), (0.5, "moderate"), (0.4, "moderate"), (0.1, "low"), (0.0, "low")],
)
def test_risk_category_thresholds(probability, expected):
    assert _risk_category(probability) == expected


@pytest.mark.parametrize("probability,expected", [(0.5, 0.0), (1.0, 1.0), (0.0, 1.0), (0.75, 0.5)])
def test_confidence_score(probability, expected):
    assert _confidence_score(probability) == pytest.approx(expected)


def test_predict_and_explain_returns_full_response_shape(runtime, raw_patient_record):
    response = predict_and_explain(runtime, raw_patient_record)

    assert set(response.keys()) == {
        "predicted_admission",
        "admission_probability",
        "confidence_score",
        "risk_category",
        "base_rate_probability",
        "features_that_increased_risk",
        "features_that_decreased_risk",
        "model_name",
        "model_version",
        "processing_time_ms",
    }
    assert response["model_name"] == "lightgbm"
    assert response["risk_category"] in {"low", "moderate", "high"}
    assert response["processing_time_ms"] > 0
