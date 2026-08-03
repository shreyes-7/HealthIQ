from fastapi.testclient import TestClient

from Backend.app.main import app
from Backend.app.services.explanation_service import ExplanationRuntime


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_lifespan_loads_explanation_runtime_once():
    with TestClient(app) as client:
        assert isinstance(client.app.state.explanation_runtime, ExplanationRuntime)


def test_docs_are_served():
    with TestClient(app) as client:
        response = client.get("/docs")

    assert response.status_code == 200
