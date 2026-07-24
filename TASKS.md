# TASKS.md

# AI Agent Workflow

## Before Starting

1. Read `CLAUDE.md` completely.
2. Read this `TASKS.md` completely.
3. Inspect the repository structure and existing code.
4. If this is the first interaction in a new conversation, read `Docs/PROJECT_BRIEF.md`.
5. Read `Docs/PROJECT_CONTEXT.md` **only if** additional project details are required or the current task references it.

---

## While Working

1. Work on **only the first incomplete milestone**.
2. Do not skip milestones unless explicitly instructed.
3. Do not modify unrelated files.
4. Never overwrite raw data.
5. Follow the coding standards defined in `CLAUDE.md`.
6. Reuse existing code before creating new modules.
7. Keep the implementation modular, documented, and production-ready.
8. Ask for clarification if requirements are ambiguous instead of making assumptions.

---

## Before Finishing

1. Verify that the milestone is fully completed.
2. Run relevant tests or validation checks where applicable.
3. Update the milestone status in `TASKS.md`.
4. Summarize:
   - What was completed
   - Files created or modified
   - Key implementation decisions
   - Any blockers or assumptions
5. Stop and wait for the next instruction.

# Sprint 1 - Machine Learning Data Pipeline

Status: 🚧 In Progress

Owner: ML Team

Goal:
Build a completely reproducible data pipeline that transforms the raw NHAMCS 2022 Emergency Department dataset into a clean, model-ready dataset suitable for machine learning.

The output of this sprint should be reusable by all future machine learning models without modifying the preprocessing code.

---

# Milestone 1 — Dataset Setup

## Objectives

- [ ] Create ML project directory structure
- [ ] Place raw NHAMCS dataset in `data/raw`
- [ ] Store NHAMCS documentation in `docs/dataset`
- [ ] Create configuration file for dataset paths
- [ ] Verify dataset integrity
- [ ] Verify dataset can be loaded correctly
- [ ] Record dataset metadata

Deliverables

- Dataset Loader
- Dataset Metadata
- Configuration File

Status

⬜ Not Started

---

# Milestone 2 — Dataset Understanding

## Objectives

Generate a complete understanding of the dataset before modifying any data.

Tasks

- [ ] Determine dataset dimensions
- [ ] Count rows
- [ ] Count columns
- [ ] Identify feature types
- [ ] Separate numerical and categorical variables
- [ ] Identify datetime variables
- [ ] Identify identifier columns
- [ ] Identify survey design variables
- [ ] Identify target variable
- [ ] Generate data dictionary
- [ ] Generate feature summary

Deliverables

- Dataset Report
- Feature Report
- Data Dictionary

Status

⬜ Not Started

---

# Milestone 3 — Exploratory Data Analysis

## Objectives

Understand data quality and feature distributions.

Tasks

### Missing Values

- [ ] Missing value count
- [ ] Missing value percentage
- [ ] Missing value heatmap

### Class Distribution

- [ ] Admission distribution
- [ ] Class imbalance

### Numerical Features

- [ ] Summary statistics
- [ ] Histograms
- [ ] Density plots
- [ ] Boxplots
- [ ] Outlier analysis

### Categorical Features

- [ ] Frequency tables
- [ ] Category counts
- [ ] Rare category detection

### Correlation

- [ ] Correlation matrix
- [ ] Highly correlated features

### Survey Variables

- [ ] Understand survey weights
- [ ] Understand strata
- [ ] Understand PSU

Deliverables

- Complete EDA Notebook
- Visualizations
- EDA Report

Status

⬜ Not Started

---

# Milestone 4 — Data Cleaning

## Objectives

Clean the dataset while preserving useful information.

Tasks

### Remove Problems

- [ ] Duplicate rows
- [ ] Duplicate columns
- [ ] Invalid values
- [ ] Impossible values

### Missing Values

- [ ] Numerical imputation strategy
- [ ] Categorical imputation strategy
- [ ] Drop high-missing columns if justified

### Data Types

- [ ] Convert incorrect datatypes
- [ ] Normalize categorical values
- [ ] Convert boolean variables
- [ ] Convert numeric variables

### Feature Cleanup

- [ ] Remove constant columns
- [ ] Remove near-zero variance columns
- [ ] Remove irrelevant identifiers

Deliverables

- Clean Dataset

Status

⬜ Not Started

---

# Milestone 5 — Feature Engineering

## Objectives

Prepare meaningful features for prediction.

Tasks

### Encoding

- [ ] Label Encoding
- [ ] One Hot Encoding
- [ ] Ordinal Encoding where appropriate

### Numerical Processing

- [ ] Scaling
- [ ] Normalization
- [ ] Standardization

### Feature Creation

- [ ] Derived clinical features
- [ ] Combined features
- [ ] Interaction features

### Feature Reduction

- [ ] Remove redundant variables
- [ ] Remove highly correlated variables

Deliverables

- Feature Engineered Dataset

Status

⬜ Not Started

---

# Milestone 6 — Feature Selection

## Objectives

Identify the best predictive variables.

Tasks

- [ ] Variance Threshold
- [ ] Correlation Analysis
- [ ] Mutual Information
- [ ] Tree-based Importance
- [ ] Recursive Feature Elimination
- [ ] Clinical relevance review

Deliverables

- Selected Feature List

Status

⬜ Not Started

---

# Milestone 7 — Train/Test Preparation

## Objectives

Prepare reproducible datasets.

Tasks

- [ ] Define target variable
- [ ] Split train/validation/test
- [ ] Preserve class balance
- [ ] Preserve preprocessing pipeline

Deliverables

- Train Dataset
- Validation Dataset
- Test Dataset

Status

⬜ Not Started

---

# Milestone 8 — Survey-Aware Preparation

## Objectives

Prepare NHAMCS survey information.

Tasks

- [ ] Identify survey weights
- [ ] Identify strata
- [ ] Identify PSU
- [ ] Preserve survey variables
- [ ] Build survey-aware preprocessing pipeline

Deliverables

- Survey Dataset

Status

⬜ Not Started

---

# Milestone 9 — Pipeline Development

## Objectives

Create reusable preprocessing pipeline.

Tasks

- [ ] Data Loader
- [ ] Validator
- [ ] Cleaner
- [ ] Encoder
- [ ] Scaler
- [ ] Feature Selector
- [ ] Pipeline Configuration

Deliverables

- preprocessing_pipeline.py

Status

⬜ Not Started

---

# Milestone 10 — Save Artifacts

## Objectives

Persist all preprocessing artifacts.

Tasks

- [ ] Save encoder
- [ ] Save scaler
- [ ] Save feature names
- [ ] Save preprocessing pipeline
- [ ] Save metadata

Deliverables

saved_models/

├── encoder.pkl

├── scaler.pkl

├── preprocessing.pkl

├── feature_names.json

├── metadata.json

Status

⬜ Not Started

---

# Milestone 11 — Validation

## Objectives

Verify preprocessing correctness.

Tasks

- [ ] No missing values remain
- [ ] Correct datatypes
- [ ] Correct feature dimensions
- [ ] Pipeline reproducibility
- [ ] Pipeline unit tests

Deliverables

Validation Report

Status

⬜ Not Started

---

# Milestone 12 — Ready for Modeling

The preprocessing phase is complete when:

- [ ] Dataset is clean
- [ ] Dataset is reproducible
- [ ] Features are engineered
- [ ] Selected features finalized
- [ ] Train/Test datasets saved
- [ ] Survey variables preserved
- [ ] Pipeline saved
- [ ] Encoder saved
- [ ] Scaler saved
- [ ] Metadata saved
- [ ] Ready for Logistic Regression
- [ ] Ready for Random Forest
- [ ] Ready for XGBoost
- [ ] Ready for LightGBM
- [ ] Ready for CatBoost

Status

⬜ Not Started

---

# Sprint Deliverables

By the end of Sprint 1, the repository should contain:

ml/

├── preprocessing/

├── feature_engineering/

├── survey/

├── utils/

├── configs/

├── notebooks/

└── saved_models/

Generated artifacts:

- Clean Dataset
- Processed Dataset
- Train Dataset
- Validation Dataset
- Test Dataset
- Preprocessing Pipeline
- Encoder
- Scaler
- Feature Metadata
- Data Dictionary
- EDA Report
- Validation Report

Sprint Status

Progress: 0%

Current Task:
Dataset Setup