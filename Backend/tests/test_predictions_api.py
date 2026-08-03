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


def test_predict_persists_a_retrievable_history_record():
    with TestClient(app) as client:
        predict_response = client.post("/api/v1/predict", json=VALID_PAYLOAD)
        assert predict_response.status_code == 200

        history_response = client.get("/api/v1/predictions", params={"limit": 1})

    assert history_response.status_code == 200
    body = history_response.json()
    assert body["status"] == "success"
    latest = body["data"][0]
    assert latest["model_name"] == "lightgbm"
    assert latest["risk_category"] in {"low", "moderate", "high"}
    assert isinstance(latest["top_contributing_features"], list)


def test_predictions_history_respects_limit():
    with TestClient(app) as client:
        client.post("/api/v1/predict", json=VALID_PAYLOAD)
        client.post("/api/v1/predict", json=VALID_PAYLOAD)

        response = client.get("/api/v1/predictions", params={"limit": 1})

    assert len(response.json()["data"]) == 1
