"""Sprint 3 Milestone 7: Explanation Validation.

Verifies the explanations produced by Milestones 2-6 are trustworthy:
SHAP values reconstruct actual model predictions (on the FULL validation
split, not a spot-check), feature ordering is consistent, explanations
are deterministic/reproducible, the preprocessing pipeline handoff is
still clean, and no SHAP value is missing.

No model is retrained here -- only validated.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_explanation_validation
"""

import logging
from datetime import datetime, timezone

import joblib
import numpy as np

from ML.explainability.artifacts import load_feature_names, load_model, load_preprocessing_pipeline, load_split, split_features_and_target
from ML.explainability.validation import (
    verify_explanation_stability,
    verify_feature_ordering_consistency,
    verify_no_missing_shap_values,
    verify_no_preprocessing_mismatch,
    verify_shap_reproduces_predictions,
)
from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config, resolve_repo_path
from ML.ingestion.loader import load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
PREPROCESSING_CHECK_SAMPLE_SIZE = 100


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 7 - Explanation Validation")

    feature_names = load_feature_names()
    shap_values = np.load(EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy")
    model = load_model()
    explainer = joblib.load(SAVED_MODELS_DIR / "shap_explainer.pkl")
    expected_value = float(np.asarray(explainer.expected_value).reshape(-1)[0])

    validation_split = load_split("validation")
    validation_features, _target = split_features_and_target(validation_split)
    validation_features = validation_features[feature_names]

    checks = []

    checks.append(verify_shap_reproduces_predictions(shap_values, expected_value, model, validation_features))
    checks.append(verify_feature_ordering_consistency(shap_values, feature_names, validation_features))
    checks.append(verify_explanation_stability(explainer, validation_features))
    checks.append(verify_no_missing_shap_values(shap_values))

    pipeline = load_preprocessing_pipeline()
    config = load_config(DEFAULT_CONFIG_PATH)
    raw_dataframe, _metadata = load_dataset(config)
    raw_sample = raw_dataframe.head(PREPROCESSING_CHECK_SAMPLE_SIZE).reset_index(drop=True)
    checks.append(verify_no_preprocessing_mismatch(pipeline, model, feature_names, raw_sample))

    for check in checks:
        logger.info("[%s] %s: %s", "PASS" if check["passed"] else "FAIL", check["check"], {k: v for k, v in check.items() if k not in ("check", "passed")})

    all_passed = all(check["passed"] for check in checks)
    write_report(checks, all_passed)

    logger.info(
        "Sprint 3 Milestone 7 %s",
        "PASSED - explanations are validated and trustworthy" if all_passed else "FAILED - see validation_report.md",
    )


def write_report(checks: list[dict], all_passed: bool) -> None:
    lines = [
        "# Explanation Validation Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## Overall: {'VALID' if all_passed else 'INVALID — see failures below'}",
        "",
        "## Checks",
        "",
    ]
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        lines.append(f"### [{status}] `{check['check']}`")
        lines.append("")
        for key, value in check.items():
            if key in ("check", "passed"):
                continue
            lines.append(f"- {key}: `{value}`")
        lines.append("")

    lines += [
        "## Limitations",
        "",
        "- `shap_values_reproduce_predictions` and `no_missing_shap_values` were checked on the "
        "full validation split (2,404 rows); `explanation_stability` and "
        "`no_preprocessing_mismatch` were checked on smaller samples (100 rows each) for "
        "runtime reasons — TreeExplainer's determinism is a property of the algorithm "
        "(exact tree-path-dependent computation, no sampling), not data-dependent, so a small "
        "sample is sufficient to catch a configuration problem if one existed.",
        "- These checks validate SHAP's **internal mathematical consistency** with the model "
        "(values sum correctly, ordering is stable, nothing is missing) and the **preprocessing "
        "handoff** (raw data still transforms into the exact schema the model expects). They do "
        "NOT validate that the underlying model itself is clinically correct or unbiased — that "
        "is a separate, ongoing concern addressed partially by the clinical-plausibility "
        "cross-checks in Milestones 3 and 6, not resolved by this milestone alone.",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "explanation_validation_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
