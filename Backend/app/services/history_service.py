"""Persists and retrieves prediction history. All database access is
isolated here -- routes never touch the session or issue SQL directly.
"""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from Backend.app.models.prediction import PredictionRecord


def record_prediction(db_session: Session, prediction: dict) -> PredictionRecord:
    """prediction: the dict produced by
    Backend.app.services.prediction_service.predict_and_explain()."""
    top_contributing_features = (
        prediction["features_that_increased_risk"][:3] + prediction["features_that_decreased_risk"][:3]
    )

    record = PredictionRecord(
        model_name=prediction["model_name"],
        model_version=prediction["model_version"],
        predicted_admission=prediction["predicted_admission"],
        admission_probability=prediction["admission_probability"],
        confidence_score=prediction["confidence_score"],
        risk_category=prediction["risk_category"],
        processing_time_ms=prediction["processing_time_ms"],
        top_contributing_features=json.dumps(top_contributing_features),
    )

    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


def list_predictions(db_session: Session, limit: int = 50) -> list[PredictionRecord]:
    statement = select(PredictionRecord).order_by(PredictionRecord.created_at.desc()).limit(limit)
    return list(db_session.scalars(statement))
