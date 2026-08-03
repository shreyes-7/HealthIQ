"""Health monitoring endpoints. Each checks exactly one dependency so a
deployment can tell liveness, model availability, and database
availability apart -- per PROJECT_CONTEXT.md Section 67.
"""

from fastapi import APIRouter, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from Backend.app.core.exceptions import DatabaseUnavailableError, ModelUnavailableError
from Backend.app.db.session import SessionLocal
from Backend.app.schemas.common import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Liveness check", description="Confirms the application process is running.")
def liveness() -> SuccessResponse[dict]:
    return SuccessResponse(message="Service is running.", data={"status": "ok"})


@router.get(
    "/model",
    summary="Model health check",
    description="Confirms the production model, preprocessing pipeline, and SHAP explainer are loaded.",
    responses={503: {"model": ErrorResponse, "description": "The model has not finished loading."}},
)
def model_health(request: Request) -> SuccessResponse[dict]:
    runtime = getattr(request.app.state, "explanation_runtime", None)
    if runtime is None:
        raise ModelUnavailableError("The prediction model has not finished loading.")

    return SuccessResponse(
        message="Model is loaded.",
        data={"model_name": runtime.model_name, "model_version": runtime.model_version},
    )


@router.get(
    "/db",
    summary="Database health check",
    description="Confirms the configured database is reachable.",
    responses={503: {"model": ErrorResponse, "description": "The database is not reachable."}},
)
def database_health() -> SuccessResponse[dict]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise DatabaseUnavailableError() from exc

    return SuccessResponse(message="Database is reachable.", data={"status": "ok"})
