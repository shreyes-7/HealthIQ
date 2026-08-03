import pytest
from pydantic import ValidationError

from Backend.app.schemas.prediction import PredictionResponse

SAMPLE_PAYLOAD = {
    "predicted_admission": False,
    "admission_probability": 0.109,
    "confidence_score": 0.782,
    "risk_category": "low",
    "base_rate_probability": 0.15,
    "features_that_increased_risk": [
        {"feature": "CONSULT__Yes", "source_variable": "CONSULT", "feature_value": 1.0, "shap_value": 2.64}
    ],
    "features_that_decreased_risk": [
        {"feature": "AGE", "source_variable": "AGE", "feature_value": -0.5, "shap_value": -1.2}
    ],
    "model_name": "lightgbm",
    "model_version": "1.0.0",
    "processing_time_ms": 1350.4,
}


def test_prediction_response_accepts_service_layer_output():
    response = PredictionResponse(**SAMPLE_PAYLOAD)

    assert response.risk_category == "low"
    assert response.features_that_increased_risk[0].feature == "CONSULT__Yes"


def test_prediction_response_rejects_invalid_risk_category():
    payload = {**SAMPLE_PAYLOAD, "risk_category": "extreme"}

    with pytest.raises(ValidationError):
        PredictionResponse(**payload)


def test_prediction_response_rejects_out_of_range_probability():
    payload = {**SAMPLE_PAYLOAD, "admission_probability": 1.5}

    with pytest.raises(ValidationError):
        PredictionResponse(**payload)
