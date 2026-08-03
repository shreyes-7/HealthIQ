"""Application-specific exceptions and their FastAPI handlers.

Every error response -- a validation failure, a known application error,
or a genuinely unexpected exception -- returns the same `ErrorResponse`
envelope (Backend.app.schemas.common) with an appropriate HTTP status
code, and never leaks a stack trace or internal file path to the client
(CLAUDE.md: "avoid exposing internal implementation details").
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from Backend.app.core.logging import get_logger
from Backend.app.schemas.common import ErrorDetail, ErrorResponse

logger = get_logger()


class AppError(Exception):
    """Base class for every application-raised (as opposed to
    unexpected) error. Subclasses set status_code/default_message to pick
    the error category, per CLAUDE.md's "errors should be categorized"."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class ModelUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_message = "The prediction model is not available."


class DatabaseUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_message = "The database is not reachable."


class PredictionError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Failed to generate a prediction."


def _error_response(status_code: int, message: str, errors: list[ErrorDetail] | None = None) -> JSONResponse:
    body = ErrorResponse(message=message, errors=errors or [])
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    """Registered once from app/main.py. Order matters to FastAPI only in
    that more specific handlers (AppError, RequestValidationError) are
    declared before the catch-all Exception handler."""

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            ErrorDetail(field=".".join(str(part) for part in error["loc"]), message=error["msg"])
            for error in exc.errors()
        ]
        return _error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, "Request validation failed.", errors)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("Application error on %s: %s", request.url.path, exc.message)
        return _error_response(exc.status_code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _error_response(exc.status_code, str(exc.detail))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "An unexpected internal error occurred.")
