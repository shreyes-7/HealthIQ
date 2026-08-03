"""Read access to prediction history. No business logic here -- receive
request, call the service, return response.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from Backend.app.db.session import get_db_session
from Backend.app.schemas.common import ErrorResponse, SuccessResponse
from Backend.app.schemas.history import PredictionHistoryItem
from Backend.app.services import history_service

router = APIRouter(prefix="/predictions", tags=["prediction-history"])


@router.get(
    "",
    response_model=SuccessResponse[list[PredictionHistoryItem]],
    summary="List prediction history",
    description=(
        "Returns previously served predictions, most recent first. Does not include the original patient "
        "input (age/vitals/etc.) -- only the prediction outcome and its top contributing SHAP features -- "
        "per PROJECT_CONTEXT.md Section 64."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "limit was out of the allowed range."},
        503: {"model": ErrorResponse, "description": "The database is not currently available."},
    },
)
def list_predictions(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of records to return, most recent first."),
    db_session: Session = Depends(get_db_session),
) -> SuccessResponse[list[PredictionHistoryItem]]:
    records = history_service.list_predictions(db_session, limit=limit)

    return SuccessResponse(
        message="Prediction history retrieved successfully.",
        data=[PredictionHistoryItem.model_validate(record) for record in records],
    )
