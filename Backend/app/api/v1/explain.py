"""Global explainability endpoint. Serves Sprint 3's precomputed
validation-split SHAP importance -- never recomputes it per request.
"""

from fastapi import APIRouter, Query, Request

from Backend.app.core.exceptions import ModelUnavailableError
from Backend.app.schemas.common import ErrorResponse, SuccessResponse
from Backend.app.schemas.explanation import GlobalExplanationResponse

router = APIRouter(prefix="/explain", tags=["explainability"])


@router.get(
    "/global",
    response_model=SuccessResponse[GlobalExplanationResponse],
    summary="Get global feature importance",
    description=(
        "Returns Sprint 3's precomputed mean |SHAP| feature importance, computed once over the "
        "validation split -- this is never recomputed per request, since global importance is a "
        "property of the whole model, not of any single prediction."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "top_n was out of the allowed range."},
        503: {"model": ErrorResponse, "description": "The model is not currently available."},
    },
)
def get_global_explanation(
    request: Request, top_n: int = Query(20, ge=1, le=866, description="Number of top features to return.")
) -> SuccessResponse[GlobalExplanationResponse]:
    runtime = getattr(request.app.state, "explanation_runtime", None)
    if runtime is None:
        raise ModelUnavailableError("The prediction model has not finished loading.")

    result = runtime.global_explanation(top_n=top_n)

    return SuccessResponse(
        message="Global explanation retrieved successfully.",
        data=GlobalExplanationResponse(**result),
    )
