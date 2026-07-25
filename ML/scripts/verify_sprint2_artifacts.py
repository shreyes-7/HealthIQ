"""Sprint 3 Milestone 1: Verify Sprint 2 Artifacts.

Confirms every artifact the explainability sprint depends on exists,
loads correctly, and is mutually consistent -- especially that the
feature columns produced by the fitted PreprocessingPipeline exactly
match what the selected model was trained on, in the same order. SHAP
values are positional (one value per feature column, in order); a silent
mismatch here would produce wrong attributions later without any obvious
error, so this is a real check, not a formality.

No model is retrained here -- only loaded.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.verify_sprint2_artifacts
"""

import logging
from datetime import datetime, timezone

from ML.explainability.artifacts import (
    load_feature_names,
    load_model,
    load_model_metadata,
    load_preprocessing_pipeline,
    load_split,
    split_features_and_target,
)
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
PREPROCESSING_COMPATIBILITY_SAMPLE_SIZE = 50


def record_check(name: str, passed: bool, detail: str = "") -> dict:
    return {"check": name, "passed": bool(passed), "detail": detail}


def main() -> bool:
    logger.info("Starting Sprint 3 Milestone 1 - Verify Sprint 2 Artifacts")
    EXPLAINABILITY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks = []
    pipeline = model = feature_names = metadata = None
    splits = {}

    # 1. Load preprocessing pipeline
    try:
        pipeline = load_preprocessing_pipeline()
        checks.append(record_check("load_preprocessing_pipeline", pipeline.is_fitted))
    except Exception as error:
        checks.append(record_check("load_preprocessing_pipeline", False, str(error)))
    logger.info("[%s] load_preprocessing_pipeline", "PASS" if checks[-1]["passed"] else "FAIL")

    # 2. Load best trained model
    try:
        model = load_model()
        checks.append(record_check("load_best_model", model is not None, type(model).__name__))
    except Exception as error:
        checks.append(record_check("load_best_model", False, str(error)))
    logger.info("[%s] load_best_model", "PASS" if checks[-1]["passed"] else "FAIL")

    # 3. Load feature metadata
    try:
        feature_names = load_feature_names()
        metadata = load_model_metadata()
        checks.append(
            record_check(
                "load_feature_metadata",
                len(feature_names) == metadata["feature_count"],
                f"{len(feature_names)} features (metadata claims {metadata.get('feature_count')})",
            )
        )
    except Exception as error:
        checks.append(record_check("load_feature_metadata", False, str(error)))
        feature_names = feature_names or []
        metadata = metadata or {}
    logger.info("[%s] load_feature_metadata", "PASS" if checks[-1]["passed"] else "FAIL")

    # 4-6. Load train/validation/test
    for split_name in ("train", "validation", "test"):
        try:
            frame = load_split(split_name)
            splits[split_name] = frame
            checks.append(record_check(f"load_{split_name}_dataset", len(frame) > 0, str(frame.shape)))
        except Exception as error:
            checks.append(record_check(f"load_{split_name}_dataset", False, str(error)))
        logger.info("[%s] load_%s_dataset", "PASS" if checks[-1]["passed"] else "FAIL", split_name)

    # 7. Verify feature ordering: train split columns, and the model's own
    # recollection of what it was trained on (LightGBM's sklearn wrapper
    # stores this), must both match feature_names.json exactly.
    if "train" in splits and feature_names:
        train_features, _ = split_features_and_target(splits["train"])
        order_matches = list(train_features.columns) == feature_names
        checks.append(record_check("feature_ordering_matches_train_split", order_matches))
        logger.info("[%s] feature_ordering_matches_train_split", "PASS" if order_matches else "FAIL")

        if model is not None and hasattr(model, "feature_name_"):
            model_order_matches = list(model.feature_name_) == feature_names
            checks.append(record_check("feature_ordering_matches_model_booster", model_order_matches))
            logger.info("[%s] feature_ordering_matches_model_booster", "PASS" if model_order_matches else "FAIL")

    # 8. Verify preprocessing compatibility: run the pipeline fresh on a raw
    # sample and confirm it reproduces the exact feature schema the model
    # expects. This is the true end-to-end check -- raw row in, correctly
    # shaped features out, ready for the model.
    if pipeline is not None and feature_names:
        try:
            config = load_config(DEFAULT_CONFIG_PATH)
            raw_dataframe, _metadata = load_dataset(config)
            sample = raw_dataframe.head(PREPROCESSING_COMPATIBILITY_SAMPLE_SIZE).reset_index(drop=True)
            result = pipeline.transform(sample)
            schema_matches = list(result["features"].columns) == feature_names
            checks.append(record_check("preprocessing_output_matches_model_features", schema_matches))
            logger.info(
                "[%s] preprocessing_output_matches_model_features",
                "PASS" if schema_matches else "FAIL",
            )

            if schema_matches and model is not None:
                predictions = model.predict_proba(result["features"])[:, 1]
                predict_ok = len(predictions) == len(sample) and not any(
                    p != p for p in predictions  # NaN check without numpy import
                )
                checks.append(record_check("model_predicts_on_pipeline_output", predict_ok))
                logger.info("[%s] model_predicts_on_pipeline_output", "PASS" if predict_ok else "FAIL")
        except Exception as error:
            checks.append(record_check("preprocessing_output_matches_model_features", False, str(error)))
            logger.info("[FAIL] preprocessing_output_matches_model_features: %s", error)

    all_passed = all(check["passed"] for check in checks)
    write_readiness_report(checks, all_passed, metadata or {})

    logger.info(
        "Sprint 3 Milestone 1 %s",
        "PASSED - all artifacts verified, ready for SHAP integration" if all_passed else "FAILED - see report",
    )
    return all_passed


def write_readiness_report(checks: list[dict], all_passed: bool, metadata: dict) -> None:
    lines = [
        "# Explainability Readiness Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## Overall: {'READY' if all_passed else 'NOT READY'}",
        "",
        f"Selected model: `{metadata.get('model_name', 'unknown')}` "
        f"(version {metadata.get('version', 'unknown')}, {metadata.get('feature_count', '?')} features)",
        "",
        "No model was retrained. All artifacts below were loaded, not regenerated.",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        detail = f" — {check['detail']}" if check.get("detail") else ""
        lines.append(f"- [{status}] `{check['check']}`{detail}")

    lines += [
        "",
        "## Notes",
        "",
        "- `feature_ordering_matches_model_booster` and "
        "`model_predicts_on_pipeline_output` are the checks that matter most for SHAP "
        "correctness: SHAP values are positional (one value per feature column, in the "
        "order the model was trained on), so any ordering drift between the pipeline's "
        "output and the model's expectation would silently misattribute every explanation.",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "explainability_readiness_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
