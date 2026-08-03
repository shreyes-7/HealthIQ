from fastapi.testclient import TestClient

from Backend.app.main import app


def test_liveness():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"


def test_model_health_reports_loaded_model():
    with TestClient(app) as client:
        response = client.get("/health/model")

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["model_name"] == "lightgbm"
    assert body["model_version"] == "1.0.0"


def test_model_health_reports_unavailable_when_runtime_missing():
    with TestClient(app) as client:
        del client.app.state.explanation_runtime
        response = client.get("/health/model")

    assert response.status_code == 503
    assert response.json()["status"] == "error"


def test_db_health_reports_reachable():
    with TestClient(app) as client:
        response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
