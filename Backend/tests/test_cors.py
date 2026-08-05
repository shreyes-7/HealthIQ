from fastapi.testclient import TestClient

from Backend.app.main import app


def test_allows_configured_frontend_origin():
    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_preflight_request_is_allowed_for_configured_origin():
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/predict",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_rejects_unconfigured_origin():
    with TestClient(app) as client:
        response = client.get("/health", headers={"Origin": "http://evil.example.com"})

    assert response.status_code == 200  # request succeeds, but without CORS headers granting access
    assert "access-control-allow-origin" not in response.headers
