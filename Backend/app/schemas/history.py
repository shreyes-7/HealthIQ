"""Response schema for prediction history records."""

import json
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from Backend.app.schemas.prediction import FeatureContribution


class PredictionHistoryItem(BaseModel):
    id: str
    created_at: datetime
    model_name: str
    model_version: str
    predicted_admission: bool
    admission_probability: float = Field(..., ge=0.0, le=1.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    risk_category: Literal["low", "moderate", "high"]
    processing_time_ms: float
    top_contributing_features: list[FeatureContribution]

    model_config = {"from_attributes": True}

    @field_validator("top_contributing_features", mode="before")
    @classmethod
    def _parse_json_if_needed(cls, value):
        """The ORM stores this column as a JSON-encoded string (SQLite/
        Postgres-agnostic); decode it before Pydantic validates the list."""
        if isinstance(value, str):
            return json.loads(value)
        return value
