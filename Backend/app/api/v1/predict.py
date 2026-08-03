"""Prediction endpoint. Receives request, validates, calls the service
layer, returns response -- no business logic lives here.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from Backend.app.core.exceptions import DatabaseUnavailableError, ModelUnavailableError, PredictionError
from Backend.app.core.logging import get_logger
from Backend.app.db.session import get_db_session
from Backend.app.schemas.common import ErrorResponse, SuccessResponse
from Backend.app.schemas.patient import PatientRecordRequest
from Backend.app.schemas.prediction import PredictionResponse
from Backend.app.services import history_service, prediction_service
from Backend.app.services.patient_record_assembler import PatientRecordAssembler

router = APIRouter(prefix="/predict", tags=["prediction"])
logger = get_logger()

_assembler = PatientRecordAssembler()


@router.post(
    "",
    response_model=SuccessResponse[PredictionResponse],
    summary="Predict Emergency Department admission",
    description=(
        "Runs a curated patient record through the production LightGBM model and returns an admission "
        "prediction together with its SHAP-based explanation in a single response -- per CLAUDE.md, a "
        "prediction is never returned without an explanation. Fields the client omits are filled by the "
        "same fitted imputation the training pipeline used for any other missing value."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Request validation failed (missing/invalid/unexpected field)."},
        500: {"model": ErrorResponse, "description": "The model failed to produce a prediction for this record."},
        503: {"model": ErrorResponse, "description": "The model or database is not currently available."},
    },
)
def predict(
    payload: PatientRecordRequest, request: Request, db_session: Session = Depends(get_db_session)
) -> SuccessResponse[PredictionResponse]:
    """Per CLAUDE.md, every prediction is returned together with its
    explanation -- there is no prediction-only response shape."""
    runtime = getattr(request.app.state, "explanation_runtime", None)
    if runtime is None:
        raise ModelUnavailableError("The prediction model has not finished loading.")

    raw_record = _assembler.assemble(payload)

    try:
        result = prediction_service.predict_and_explain(runtime, raw_record)
    except Exception as exc:
        raise PredictionError("Failed to generate a prediction for the given patient record.") from exc

    try:
        history_service.record_prediction(db_session, result)
    except SQLAlchemyError as exc:
        raise DatabaseUnavailableError("Prediction succeeded but could not be saved to prediction history.") from exc

    # Never log the request payload itself (age/vitals/demographics) --
    # only prediction metadata, per CLAUDE.md's logging guidance.
    logger.info(
        "Prediction served: model_version=%s risk_category=%s admission_probability=%.4f processing_time_ms=%.1f",
        result["model_version"],
        result["risk_category"],
        result["admission_probability"],
        result["processing_time_ms"],
    )

    return SuccessResponse(
        message="Prediction generated successfully.",
        data=PredictionResponse(**result),
    )
