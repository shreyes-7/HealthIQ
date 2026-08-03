from fastapi.testclient import TestClient

from Backend.app.main import app

VALID_PAYLOAD = {
    "age": 67,
    "sex": 2,
    "pulse": 88,
    "temperature_fahrenheit": 98.6,
    "respiratory_rate": 18,
    "systolic_bp": 130,
    "diastolic_bp": 80,
    "triage_level": 2,
    "arrived_by_ambulance": True,
}


def test_predict_returns_prediction_with_explanation():
    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=VALID_PAYLOAD)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert 0.0 <= body["data"]["admission_probability"] <= 1.0
    assert body["data"]["risk_category"] in {"low", "moderate", "high"}
    assert body["data"]["features_that_increased_risk"]
    assert body["data"]["model_name"] == "lightgbm"


def test_predict_rejects_missing_required_field():
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "age"}

    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_out_of_range_value():
    payload = {**VALID_PAYLOAD, "age": 500}

    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422


def test_predict_rejects_unexpected_field():
    payload = {**VALID_PAYLOAD, "not_a_real_field": 1}

    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422
