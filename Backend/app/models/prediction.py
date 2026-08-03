"""The prediction history entity, per PROJECT_CONTEXT.md Section 64:
prediction id, timestamp, model version, prediction probability,
prediction outcome, explanation reference, processing time.

Deliberately does not store the patient input payload: CLAUDE.md's
logging guidance ("never log sensitive information") extends naturally
to persistent storage, and Section 64's field list does not call for
storing patient-submitted vitals/demographics alongside the prediction
record. `top_contributing_features` fills the "explanation reference"
role with a small, non-identifying summary of *why* the model predicted
what it did, not the patient's raw data.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from Backend.app.db.base import Base


def _generate_id() -> str:
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionRecord(Base):
    __tablename__ = "prediction_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_id)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, nullable=False, index=True)

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    predicted_admission: Mapped[bool] = mapped_column(Boolean, nullable=False)
    admission_probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(20), nullable=False)

    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)

    # JSON-encoded list of {feature, source_variable, shap_value} -- the
    # "explanation reference" required by PROJECT_CONTEXT.md Section 64.
    top_contributing_features: Mapped[str] = mapped_column(Text, nullable=False)
