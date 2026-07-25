"""Sprint 2 Milestone 12: Ready for Explainable AI (sprint completion gate).

Confirms the selected, serialized model is actually compatible with an
explainability method -- smoke-tested with SHAP, not just assumed by
model type. Building the real explainability module (SHAP summary/
waterfall/force plots, the explanation API) is the next sprint; this only
verifies the handoff is clean.

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_explainability_readiness_check
"""

import json
import logging
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import shap

from ML.feature_engineering.target import TARGET_COLUMN_NAME
from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")
MODELING_REPORTS_DIR = resolve_repo_path("ML/reports/modeling")
TRAIN_PATH = resolve_repo_path("Data/processed/train.parquet")

NON_FEATURE_COLUMNS = {TARGET_COLUMN_NAME, "PATWT", "EDWT", "CSTRATM", "CPSUM", "HOSPCODE", "PATCODE"}
BACKGROUND_SAMPLE_SIZE = 30
EXPLAIN_SAMPLE_SIZE = 3
TREE_BASED_MARKERS = ("Forest", "Boost", "Tree", "CatBoost", "LGBM", "XGB")


def run_shap_compatibility_check(model, background_sample: pd.DataFrame, explain_sample: pd.DataFrame) -> dict:
    model_type_name = type(model).__name__

    try:
        if any(marker in model_type_name for marker in TREE_BASED_MARKERS):
            explainer = shap.TreeExplainer(model)
            explainer.shap_values(explain_sample)
        elif model_type_name == "LogisticRegression":
            explainer = shap.LinearExplainer(model, background_sample)
            explainer.shap_values(explain_sample)
        else:
            # Model-agnostic fallback (e.g. a StackingClassifier meta-ensemble):
            # slower, but works for any predict_proba-compatible model.
            explainer = shap.Explainer(model.predict_proba, background_sample)
            explainer(explain_sample)

        return {"passed": True, "model_type": model_type_name, "explainer_type": type(explainer).__name__}
    except Exception as error:
        logger.exception("SHAP compatibility check failed")
        return {"passed": False, "model_type": model_type_name, "error": str(error)}


def main() -> None:
    logger.info("Starting Sprint 2 Milestone 12: Ready for Explainable AI")

    metadata = json.loads((SAVED_MODELS_DIR / "model_metadata.json").read_text())
    model = joblib.load(SAVED_MODELS_DIR / "model.pkl")

    dataframe = pd.read_parquet(TRAIN_PATH)
    feature_columns = [column for column in dataframe.columns if column not in NON_FEATURE_COLUMNS]
    features = dataframe[feature_columns]

    background_sample = features.sample(n=BACKGROUND_SAMPLE_SIZE, random_state=42)
    explain_sample = features.sample(n=EXPLAIN_SAMPLE_SIZE, random_state=7)

    shap_check = run_shap_compatibility_check(model, background_sample, explain_sample)
    logger.info("SHAP compatibility check: %s", shap_check)

    checklist = {
        "model_serialized": (SAVED_MODELS_DIR / "model.pkl").exists(),
        "model_metadata_present": (SAVED_MODELS_DIR / "model_metadata.json").exists(),
        "preprocessing_pipeline_present": (SAVED_MODELS_DIR / "preprocessing_pipeline.pkl").exists(),
        "model_comparison_complete": (MODELING_REPORTS_DIR / "model_comparison.csv").exists(),
        "survey_aware_comparison_complete": (MODELING_REPORTS_DIR / "survey_aware_comparison.md").exists(),
        "final_selection_documented": (MODELING_REPORTS_DIR / "final_model_selection.md").exists(),
        "reproducibility_validated": (MODELING_REPORTS_DIR / "validation_report.md").exists(),
        "shap_compatible": shap_check["passed"],
    }
    all_ready = all(checklist.values())

    lines = [
        "# Ready for Explainable AI — Sprint 2 Completion Gate",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## Overall: {'READY' if all_ready else 'NOT READY'}",
        "",
        f"Selected model: `{metadata['model_name']}` (version {metadata['version']})",
        "",
        "## Checklist",
        "",
    ]
    for check_name, passed in checklist.items():
        lines.append(f"- [{'x' if passed else ' '}] {check_name}")

    lines += [
        "",
        "## SHAP Compatibility Detail",
        "",
        f"```\n{shap_check}\n```",
        "",
        "This confirms the model CAN be explained; it does not build the explainability module "
        "itself (SHAP summary/waterfall/force plots, the explanation API) -- that is the next "
        "sprint's scope (PROJECT_CONTEXT.md Section 43).",
        "",
    ]

    report_path = MODELING_REPORTS_DIR / "ready_for_explainable_ai.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)

    if all_ready:
        logger.info("Sprint 2 Milestone 12 (Ready for Explainable AI) completed successfully. Sprint 2 is COMPLETE.")
    else:
        logger.error("Sprint 2 Milestone 12 gate NOT satisfied: %s", {k: v for k, v in checklist.items() if not v})


if __name__ == "__main__":
    main()
