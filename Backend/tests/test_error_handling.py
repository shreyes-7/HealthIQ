from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from Backend.app.main import app
from Backend.app.services import history_service, prediction_service

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


def test_validation_error_uses_common_error_envelope():
    payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "age"}

    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert body["message"]
    assert any(error["field"].endswith("age") for error in body["errors"])


def test_unknown_route_returns_common_error_envelope():
    with TestClient(app) as client:
        response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
    assert response.json()["status"] == "error"


def test_prediction_failure_returns_prediction_error(monkeypatch):
    def _boom(runtime, raw_record):
        raise RuntimeError("simulated ML failure")

    monkeypatch.setattr(prediction_service, "predict_and_explain", _boom)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/v1/predict", json=VALID_PAYLOAD)

    assert response.status_code == 500
    body = response.json()
    assert body["status"] == "error"
    assert "internal path" not in body["message"].lower()
    assert "traceback" not in body["message"].lower()


def test_history_persistence_failure_returns_database_unavailable_error(monkeypatch):
    def _boom(db_session, prediction):
        raise SQLAlchemyError("simulated database outage")

    monkeypatch.setattr(history_service, "record_prediction", _boom)

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/v1/predict", json=VALID_PAYLOAD)

    assert response.status_code == 503
    assert response.json()["status"] == "error"
