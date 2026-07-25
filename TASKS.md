# TASKS.md

# Sprint 3 - Explainable AI (SHAP)

Status: 🚧 In Progress

Owner: ML Team

Goal:

Develop a complete Explainable AI pipeline for the selected Emergency Department admission prediction model using SHAP.

The objective is to generate reliable global and local explanations, validate explanation quality, and prepare explainability artifacts for backend integration, frontend visualization, and research reporting.

This sprint begins only after Sprint 2 has successfully selected and serialized the production model.

---

# AI Agent Workflow

## Before Starting

1. Read `CLAUDE.md`.
2. Read this `TASKS.md`.
3. Inspect the repository.
4. Verify Sprint 2 artifacts exist.
5. Read `Docs/PROJECT_CONTEXT.md` only if additional information is required.

---

## While Working

1. Work only on the first incomplete milestone.
2. Never skip milestones.
3. Reuse preprocessing artifacts.
4. Reuse the production model selected in Sprint 2.
5. Never retrain models.
6. Keep implementations modular.
7. Produce reusable explainability utilities.
8. Save every generated visualization and report.
9. Document assumptions and limitations.

---

## Before Finishing

1. Verify milestone completion.
2. Validate generated explanations.
3. Update milestone status.
4. Summarize:
   - Completed work
   - Files created
   - Visualizations generated
   - Key observations
   - Limitations
5. Stop and wait for review.

---

# Milestone 1 — Verify Sprint 2 Artifacts

## Objectives

Ensure all required assets exist before explainability begins.

### Tasks

- [ ] Load preprocessing pipeline
- [ ] Load best trained model
- [ ] Load feature metadata
- [ ] Load train dataset
- [ ] Load validation dataset
- [ ] Load test dataset
- [ ] Verify feature ordering
- [ ] Verify preprocessing compatibility

### Deliverables

- Explainability Readiness Report

Status

⬜ Not Started

---

# Milestone 2 — SHAP Integration

## Objectives

Initialize the SHAP explainability framework.

### Tasks

- [ ] Detect model type
- [ ] Select appropriate SHAP Explainer
- [ ] Initialize explainer
- [ ] Generate SHAP values
- [ ] Verify output dimensions
- [ ] Verify runtime performance

### Deliverables

- SHAP Explainer
- SHAP Values

Status

⬜ Not Started

---

# Milestone 3 — Global Explainability

## Objectives

Understand overall model behavior.

### Tasks

Generate:

- [ ] SHAP Summary Plot
- [ ] SHAP Bar Plot
- [ ] Beeswarm Plot
- [ ] Global Feature Importance
- [ ] Mean Absolute SHAP Values

Document:

- Most influential features
- Least influential features
- Clinical interpretation

### Deliverables

reports/

global_explainability.pdf

visualizations/

summary_plot.png

bar_plot.png

beeswarm_plot.png

Status

⬜ Not Started

---

# Milestone 4 — Local Explainability

## Objectives

Explain individual patient predictions.

### Tasks

Generate:

- [ ] Waterfall Plot
- [ ] Force Plot
- [ ] Decision Plot

Explain:

- Why patient was admitted
- Which variables increased risk
- Which variables reduced risk

Test multiple patient examples.

### Deliverables

patient_explanations/

patient_1/

patient_2/

patient_3/

Status

⬜ Not Started

---

# Milestone 5 — Dependence Analysis

## Objectives

Understand feature interactions.

### Tasks

Generate SHAP Dependence Plots for:

- [ ] Top Feature
- [ ] Second Feature
- [ ] Third Feature
- [ ] Additional important variables

Identify:

- Nonlinear effects
- Threshold effects
- Feature interactions

### Deliverables

dependence_plots/

Status

⬜ Not Started

---

# Milestone 6 — Cohort Analysis

## Objectives

Compare explanations across patient groups.

### Tasks

Generate explanations by:

- [ ] Admission vs Discharge
- [ ] Age groups
- [ ] Gender
- [ ] Arrival mode
- [ ] Triage level

Compare:

- Feature importance
- SHAP distributions

### Deliverables

Cohort Explainability Report

Status

⬜ Not Started

---

# Milestone 7 — Explanation Validation

## Objectives

Ensure explanations are reliable.

### Tasks

Verify:

- [ ] SHAP values reproduce predictions
- [ ] Feature ordering consistency
- [ ] Explanation stability
- [ ] No preprocessing mismatch
- [ ] No missing SHAP values

Document limitations.

### Deliverables

Validation Report

Status

⬜ Not Started

---

# Milestone 8 — Explainability API Preparation

## Objectives

Prepare reusable utilities for backend.

### Tasks

Create reusable modules:

- [ ] SHAP Loader
- [ ] Explanation Generator
- [ ] Global Explanation Service
- [ ] Local Explanation Service
- [ ] Visualization Export Utility

Outputs:

- JSON explanations
- PNG plots
- Metadata

### Deliverables

ML/

explainability/

Status

⬜ Not Started

---

# Milestone 9 — Research Documentation

## Objectives

Prepare explainability outputs for publication.

### Tasks

Generate:

- [ ] Feature Importance Table
- [ ] Global Interpretation Report
- [ ] Local Interpretation Report
- [ ] Clinical Findings
- [ ] Limitations
- [ ] Future Work

### Deliverables

Explainability Report

Status

⬜ Not Started

---

# Milestone 10 — Ready for Backend Integration

Sprint 3 is complete when:

- [ ] SHAP integrated
- [ ] Global explanations generated
- [ ] Local explanations generated
- [ ] Dependence analysis completed
- [ ] Cohort analysis completed
- [ ] Explanations validated
- [ ] Explainability utilities created
- [ ] JSON outputs generated
- [ ] Reports completed
- [ ] Ready for FastAPI integration

Status

⬜ Not Started

---

# Sprint Deliverables

ML/

explainability/

├── explainer.py
├── shap_utils.py
├── global.py
├── local.py
├── export.py

reports/

├── explainability_report.pdf
├── validation_report.pdf

visualizations/

├── summary_plot.png
├── beeswarm_plot.png
├── bar_plot.png
├── waterfall_plot.png
├── force_plot.png
├── decision_plot.png
├── dependence_plots/

patient_explanations/

saved_models/

├── shap_explainer.pkl

Generated Artifacts

- SHAP Explainer
- SHAP Values
- Global Report
- Local Reports
- Cohort Report
- Validation Report
- Explainability Utilities
- Visualization Assets
- JSON Explanation Files

---

# Sprint Status

Progress: 0%

Current Task:

Verify Sprint 2 Artifacts