from Backend.app.schemas.common import ErrorResponse, SuccessResponse


def test_success_response_defaults():
    response = SuccessResponse(message="ok", data={"a": 1})

    assert response.status == "success"
    assert response.api_version == "v1"
    assert response.timestamp is not None


def test_error_response_defaults():
    response = ErrorResponse(message="something went wrong")

    assert response.status == "error"
    assert response.errors == []
