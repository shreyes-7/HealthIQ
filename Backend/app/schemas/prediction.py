"""Response schema for the prediction + explainability endpoint.

Mirrors the dict shape produced by
`Backend.app.services.prediction_service.predict_and_explain`, which in
turn wraps `ML.explainability.local_explanations.explain_patient_in_words`.
Every field here traces back to that function's output -- nothing is
computed independently by the schema layer.
"""

from typing import Literal

from pydantic import BaseModel, Field


class FeatureContribution(BaseModel):
    feature: str = Field(..., description="The encoded model feature name (e.g. 'CONSULT__Yes').")
    source_variable: str = Field(..., description="The raw source variable this feature was derived from (e.g. 'CONSULT').")
    feature_value: float = Field(..., description="The feature's value after encoding/scaling, as seen by the model.")
    shap_value: float = Field(..., description="This feature's SHAP contribution, in log-odds (margin) space.")


class PredictionResponse(BaseModel):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "predicted_admission": False,
                    "admission_probability": 0.109,
                    "confidence_score": 0.782,
                    "risk_category": "low",
                    "base_rate_probability": 0.150,
                    "features_that_increased_risk": [
                        {
                            "feature": "CONSULT__Yes",
                            "source_variable": "CONSULT",
                            "feature_value": 1.0,
                            "shap_value": 2.64,
                        }
                    ],
                    "features_that_decreased_risk": [
                        {"feature": "AGE", "source_variable": "AGE", "feature_value": -0.5, "shap_value": -1.2}
                    ],
                    "model_name": "lightgbm",
                    "model_version": "1.0.0",
                    "processing_time_ms": 1350.4,
                }
            ]
        }
    }

    predicted_admission: bool = Field(..., description="True if predicted probability >= 0.5.")
    admission_probability: float = Field(..., ge=0.0, le=1.0, description="Model-predicted probability of hospital admission.")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Distance from the 0.5 decision boundary, scaled to [0, 1]."
    )
    risk_category: Literal["low", "moderate", "high"] = Field(..., description="Risk category derived from admission_probability.")
    base_rate_probability: float = Field(..., description="The model's average predicted probability across the validation split.")
    features_that_increased_risk: list[FeatureContribution] = Field(
        ..., description="Top features that pushed the prediction toward admission, ranked by SHAP value."
    )
    features_that_decreased_risk: list[FeatureContribution] = Field(
        ..., description="Top features that pushed the prediction toward discharge, ranked by SHAP value."
    )
    model_name: str = Field(..., description="Name of the model that produced this prediction.")
    model_version: str = Field(..., description="Version of the model that produced this prediction.")
    processing_time_ms: float = Field(..., ge=0.0, description="Time spent generating this prediction and explanation.")
