from fastapi.testclient import TestClient

from Backend.app.main import app


def test_global_explanation_default_top_n():
    with TestClient(app) as client:
        response = client.get("/api/v1/explain/global")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert len(body["data"]["top_features"]) == 20
    assert body["data"]["computed_on"] == "validation_split"


def test_global_explanation_respects_top_n():
    with TestClient(app) as client:
        response = client.get("/api/v1/explain/global", params={"top_n": 5})

    assert response.status_code == 200
    assert len(response.json()["data"]["top_features"]) == 5


def test_global_explanation_rejects_out_of_range_top_n():
    with TestClient(app) as client:
        response = client.get("/api/v1/explain/global", params={"top_n": 0})

    assert response.status_code == 422
