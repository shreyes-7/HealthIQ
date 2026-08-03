"""Backend-owned integration point with the ML explainability layer.

Wraps ML.explainability.service.ExplanationService so the ML artifacts
(model, preprocessing pipeline, SHAP explainer, feature names) are loaded
exactly once per process -- at application startup, via the FastAPI
lifespan in app/main.py -- and reused for every request. Never reloads or
retrains per request.
"""

from __future__ import annotations

import pandas as pd

from ML.explainability.artifacts import load_model_metadata
from ML.explainability.service import ExplanationService, get_global_explanation


class ModelCompatibilityError(RuntimeError):
    """Raised at startup when the loaded model's features don't match feature_names.json."""


class ExplanationRuntime:
    """Loads every ML artifact once and exposes the operations the backend
    needs. Construction is expensive (model + pipeline + SHAP explainer
    load); this should be instantiated once per process, not per request."""

    def __init__(self) -> None:
        self._service = ExplanationService()
        self._metadata = load_model_metadata()
        self._verify_model_compatibility()

    def _verify_model_compatibility(self) -> None:
        model_features = list(getattr(self._service.model, "feature_name_", []))
        expected_features = self._service.feature_names
        if model_features and model_features != expected_features:
            raise ModelCompatibilityError(
                "The loaded model's feature_name_ does not match feature_names.json -- "
                "model.pkl and the feature metadata are out of sync."
            )

    @property
    def model_name(self) -> str:
        return self._metadata["model_name"]

    @property
    def model_version(self) -> str:
        return self._metadata["version"]

    def explain_raw_patient(self, raw_record: pd.DataFrame) -> dict:
        """raw_record: a single-row DataFrame with raw NHAMCS columns."""
        return self._service.explain_patient(raw_record)

    def global_explanation(self, top_n: int = 20) -> dict:
        return get_global_explanation(top_n=top_n)
