"""Turns a raw ML explanation into the shape the prediction API returns.

Risk-category thresholds and confidence scoring are backend business logic,
not ML logic: they are a product decision about how to present a
probability, so they live here rather than in ML/explainability.
"""

from __future__ import annotations

import time

import pandas as pd

from Backend.app.services.explanation_service import ExplanationRuntime

# (minimum probability, category) pairs, checked from highest to lowest.
RISK_CATEGORY_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (0.75, "high"),
    (0.4, "moderate"),
    (0.0, "low"),
)


def _risk_category(probability: float) -> str:
    for threshold, category in RISK_CATEGORY_THRESHOLDS:
        if probability >= threshold:
            return category
    return "low"


def _confidence_score(probability: float) -> float:
    """Distance from the decision boundary, scaled to [0, 1]: a prediction
    at 0.5 has zero confidence, a prediction at 0.0 or 1.0 has full
    confidence."""
    return abs(probability - 0.5) * 2


def predict_and_explain(runtime: ExplanationRuntime, raw_record: pd.DataFrame) -> dict:
    """raw_record: a single-row DataFrame with raw NHAMCS columns."""
    start = time.perf_counter()
    explanation = runtime.explain_raw_patient(raw_record)
    processing_time_ms = (time.perf_counter() - start) * 1000

    probability = explanation["predicted_probability"]

    return {
        "predicted_admission": explanation["predicted_admission"],
        "admission_probability": probability,
        "confidence_score": _confidence_score(probability),
        "risk_category": _risk_category(probability),
        "base_rate_probability": explanation["base_rate_probability"],
        "features_that_increased_risk": explanation["features_that_increased_risk"],
        "features_that_decreased_risk": explanation["features_that_decreased_risk"],
        "model_name": runtime.model_name,
        "model_version": runtime.model_version,
        "processing_time_ms": processing_time_ms,
    }
