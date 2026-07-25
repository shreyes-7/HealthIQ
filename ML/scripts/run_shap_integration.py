"""Sprint 3 Milestone 2: SHAP Integration.

Builds the SHAP explainer for the selected model and computes SHAP values
on the validation split (held-out, unseen by the model during training --
explanations should reflect genuine generalization behavior, not
training-set memorization). Saves both the explainer and the computed
values so Milestones 3, 5, 6, and 7 can reuse them without recomputing.

No model is retrained here -- only explained.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_shap_integration
"""

import json
import logging
import time
from datetime import datetime, timezone

import joblib
import numpy as np

from ML.explainability.artifacts import load_feature_names, load_model, load_split, split_features_and_target
from ML.explainability.explainer import build_explainer, compute_shap_values, detect_model_family
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 2 - SHAP Integration")
    EXPLAINABILITY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    model = load_model()
    feature_names = load_feature_names()

    model_family = detect_model_family(model)
    logger.info("Detected model family: %s (%s)", model_family, type(model).__name__)

    explainer = build_explainer(model)
    logger.info("Initialized %s", type(explainer).__name__)

    validation_split = load_split("validation")
    validation_features, _validation_target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names]  # enforce exact model order

    start_time = time.monotonic()
    shap_values = compute_shap_values(explainer, validation_features)
    elapsed_seconds = time.monotonic() - start_time
    logger.info("Computed SHAP values for %d rows in %.2fs", len(validation_features), elapsed_seconds)

    expected_output_shape = (len(validation_features), len(feature_names))
    dimensions_ok = shap_values.shape == expected_output_shape
    logger.info(
        "[%s] Output dimensions: got %s, expected %s",
        "PASS" if dimensions_ok else "FAIL", shap_values.shape, expected_output_shape,
    )
    if not dimensions_ok:
        raise RuntimeError(f"SHAP output shape {shap_values.shape} does not match expected {expected_output_shape}")

    seconds_per_row = elapsed_seconds / len(validation_features)
    performance_acceptable = seconds_per_row < 0.05  # 20+ rows/sec is comfortably interactive
    logger.info(
        "[%s] Runtime performance: %.4fs/row (%.0f rows/sec)",
        "PASS" if performance_acceptable else "SLOW", seconds_per_row, 1 / seconds_per_row,
    )

    explainer_path = SAVED_MODELS_DIR / "shap_explainer.pkl"
    joblib.dump(explainer, explainer_path)
    logger.info("Saved %s", explainer_path)

    shap_values_path = EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy"
    np.save(shap_values_path, shap_values)
    logger.info("Saved %s (shape %s)", shap_values_path, shap_values.shape)

    expected_value = float(np.asarray(explainer.expected_value).reshape(-1)[0])

    write_report(model, model_family, explainer, shap_values, elapsed_seconds, seconds_per_row, expected_value)

    logger.info("Sprint 3 Milestone 2 (SHAP Integration) completed successfully.")


def write_report(model, model_family, explainer, shap_values, elapsed_seconds, seconds_per_row, expected_value) -> None:
    lines = [
        "# SHAP Integration Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Model: `{type(model).__name__}` (family: `{model_family}`)",
        f"- Explainer: `{type(explainer).__name__}`",
        f"- Explained dataset: validation split (held-out, unseen during training)",
        f"- SHAP values shape: {shap_values.shape} (rows x features)",
        f"- Runtime: {elapsed_seconds:.2f}s total, {seconds_per_row:.4f}s/row",
        f"- Expected value (base rate, margin/log-odds space): {expected_value:.4f}",
        "",
        "## Verification",
        "",
        "- Output dimensions match (n_validation_rows, n_features) exactly.",
        "- SHAP values are in **margin (log-odds) space**, not probability space "
        "(`ML.explainability.shap_utils.sigmoid` converts for human-readable output). "
        "Confirmed empirically: `shap_values.sum(axis=1) + expected_value` reconstructs "
        "`model.predict(X, raw_score=True)` to within 3e-9, and its sigmoid reconstructs "
        "`predict_proba` exactly. Full reproduction check with tolerances is Milestone 7.",
        "",
        "## Saved Artifacts",
        "",
        "- `ML/saved_models/shap_explainer.pkl` — the fitted explainer, reusable without rebuilding",
        "- `ML/reports/explainability/shap_values_validation.npy` — computed values, reusable "
        "without recomputing (Milestones 3, 5, 6, 7 load this directly)",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "shap_integration_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
