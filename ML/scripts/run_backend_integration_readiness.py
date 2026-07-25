"""Sprint 3 Milestone 10: Ready for Backend Integration (sprint completion gate).

Verifies every Sprint 3 deliverable actually exists and the explanation
service is actually callable -- not just that each milestone's script
ran without error at the time. No model is retrained or re-explained;
this milestone loads and checks, exactly like Sprint 2's Milestone 12
gate did for "Ready for Explainable AI".

Run from the repository root with:
    .venv\\Scripts\\python.exe -m ML.scripts.run_backend_integration_readiness
"""

import logging
from datetime import datetime, timezone

from ML.ingestion.config import resolve_repo_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPLAINABILITY_REPORTS_DIR = resolve_repo_path("ML/reports/explainability")
SAVED_MODELS_DIR = resolve_repo_path("ML/saved_models")

REQUIRED_FILES = {
    "shap_integrated": [SAVED_MODELS_DIR / "shap_explainer.pkl", EXPLAINABILITY_REPORTS_DIR / "shap_values_validation.npy"],
    "global_explanations_generated": [
        EXPLAINABILITY_REPORTS_DIR / "global_explainability_report.md",
        EXPLAINABILITY_REPORTS_DIR / "visualizations" / "summary_plot.png",
        EXPLAINABILITY_REPORTS_DIR / "visualizations" / "bar_plot.png",
        EXPLAINABILITY_REPORTS_DIR / "visualizations" / "beeswarm_plot.png",
    ],
    "local_explanations_generated": [
        EXPLAINABILITY_REPORTS_DIR / "patient_explanations" / f"patient_{i}" / plot
        for i in (1, 2, 3)
        for plot in ("waterfall_plot.png", "force_plot.png", "decision_plot.png", "explanation.json")
    ],
    "dependence_analysis_completed": [EXPLAINABILITY_REPORTS_DIR / "dependence_analysis_report.md"],
    "cohort_analysis_completed": [EXPLAINABILITY_REPORTS_DIR / "cohort_analysis_report.md", EXPLAINABILITY_REPORTS_DIR / "cohort_analysis.json"],
    "explanations_validated": [EXPLAINABILITY_REPORTS_DIR / "explanation_validation_report.md"],
    "explainability_utilities_created": [
        resolve_repo_path("ML/explainability/service.py"),
        resolve_repo_path("ML/explainability/export.py"),
    ],
    "json_outputs_generated": [
        EXPLAINABILITY_REPORTS_DIR / "api_check_example" / "explanation.json",
        EXPLAINABILITY_REPORTS_DIR / "api_check_example" / "global_explanation.json",
    ],
    "reports_completed": [EXPLAINABILITY_REPORTS_DIR / "explainability_research_report.md"],
}


def check_files_exist() -> dict:
    results = {}
    for gate_name, paths in REQUIRED_FILES.items():
        missing = [str(path) for path in paths if not path.exists()]
        results[gate_name] = {"passed": len(missing) == 0, "missing": missing}
    return results


def check_service_callable() -> dict:
    """The real 'ready for FastAPI integration' check: does the service
    layer actually run, end to end, right now."""
    try:
        from ML.explainability.service import ExplanationService, get_global_explanation
        from ML.ingestion.config import DEFAULT_CONFIG_PATH, load_config
        from ML.ingestion.loader import load_dataset

        service = ExplanationService()
        config = load_config(DEFAULT_CONFIG_PATH)
        raw_dataframe, _metadata = load_dataset(config)
        sample = raw_dataframe.head(1).reset_index(drop=True)

        explanation = service.explain_patient(sample)
        global_explanation = get_global_explanation(top_n=5)

        passed = (
            0.0 <= explanation["predicted_probability"] <= 1.0
            and len(global_explanation["top_features"]) == 5
        )
        return {"passed": passed, "sample_probability": explanation["predicted_probability"]}
    except Exception as error:
        logger.exception("Service callability check failed")
        return {"passed": False, "error": str(error)}


def main() -> None:
    logger.info("Starting Sprint 3 Milestone 10 - Ready for Backend Integration")

    file_checks = check_files_exist()
    for gate_name, result in file_checks.items():
        logger.info("[%s] %s", "PASS" if result["passed"] else "FAIL", gate_name)

    service_check = check_service_callable()
    logger.info("[%s] ready_for_fastapi_integration: %s", "PASS" if service_check["passed"] else "FAIL", service_check)

    all_passed = all(result["passed"] for result in file_checks.values()) and service_check["passed"]

    write_report(file_checks, service_check, all_passed)

    logger.info(
        "Sprint 3 Milestone 10 %s",
        "READY - Sprint 3 is COMPLETE" if all_passed else "NOT READY - see report",
    )


def write_report(file_checks: dict, service_check: dict, all_passed: bool) -> None:
    lines = [
        "# Ready for Backend Integration — Sprint 3 Completion Gate",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"## Overall: {'READY' if all_passed else 'NOT READY'}",
        "",
        "## Checklist",
        "",
    ]
    for gate_name, result in file_checks.items():
        status = "x" if result["passed"] else " "
        lines.append(f"- [{status}] {gate_name.replace('_', ' ')}")
        if result["missing"]:
            lines.append(f"  - Missing: {result['missing']}")

    lines.append(f"- [{'x' if service_check['passed'] else ' '}] ready for FastAPI integration")

    lines += [
        "",
        "## FastAPI Integration Check Detail",
        "",
        "Not just a file-existence check: this instantiates `ExplanationService`, runs a "
        "genuinely fresh raw row through the full raw → pipeline → model → SHAP → explanation "
        "chain, and calls `get_global_explanation()` — the exact calls a FastAPI endpoint would "
        "make.",
        "",
        f"```\n{service_check}\n```",
        "",
        "## Scope for Sprint 4 (Backend Integration)",
        "",
        "`ML/explainability/service.py`'s `ExplanationService` class and `get_global_explanation()` "
        "function are the integration point — wrap them in FastAPI request handlers per "
        "PROJECT_CONTEXT.md's Backend responsibilities (routes call the service, they do not "
        "reimplement explanation logic). See Milestone 8's latency note "
        "(`explainability_api_report.md`) before committing to a response-time SLA.",
    ]

    report_path = EXPLAINABILITY_REPORTS_DIR / "ready_for_backend_integration.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", report_path)


if __name__ == "__main__":
    main()
