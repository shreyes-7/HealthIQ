"""Response schema for the precomputed global explanation endpoint.

Mirrors `ML.explainability.service.get_global_explanation`'s output --
served from Sprint 3's precomputed validation-split SHAP values, never
recomputed per request.
"""

from pydantic import BaseModel, Field


class GlobalExplanationResponse(BaseModel):
    top_features: dict[str, float] = Field(..., description="Mean |SHAP| per encoded model feature, most influential first.")
    top_source_variables: dict[str, float] = Field(
        ..., description="Mean |SHAP| aggregated per raw source variable (one-hot dummies summed back together)."
    )
    computed_on: str = Field(..., description="Which dataset split these values were computed on.")
    n_rows: int = Field(..., description="Number of rows the SHAP values were computed over.")
