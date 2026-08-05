<div align="center">

# 🩺 HealthIQ

### Survey-Aware Explainable AI for Emergency Department Admission Prediction

**A production-grade, full-stack healthcare AI platform that predicts Emergency Department admission risk from the NHAMCS dataset — and explains every single prediction with SHAP.**

*Not a black box. Not a toy demo. A research-grade, explainable clinical decision-support platform.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](#python-setup)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](#node-setup)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)](#node-setup)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.1-009688?logo=fastapi&logoColor=white)](#backend-system)
[![LightGBM](https://img.shields.io/badge/Model-LightGBM-9ACD32)](#machine-learning)
[![SHAP](https://img.shields.io/badge/Explainability-SHAP-8A2BE2)](#explainability)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-06B6D4?logo=tailwindcss&logoColor=white)](#tech-stack)
[![Tests](https://img.shields.io/badge/tests-217%20passing-brightgreen)](#testing)
[![Status](https://img.shields.io/badge/status-active%20development-blue)](#project-status)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![GitHub stars](https://img.shields.io/github/stars/shreyes-7/HealthIQ?style=social)](https://github.com/shreyes-7/HealthIQ)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Screenshots](#screenshots)
- [Demo](#demo)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Python Setup](#python-setup)
- [Node Setup](#node-setup)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Model Training](#model-training)
- [Explainability](#explainability)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Prediction Workflow](#prediction-workflow)
- [UI Pages](#ui-pages)
- [Dataset](#dataset)
- [Machine Learning](#machine-learning)
- [Explainable AI](#explainable-ai)
- [Security](#security)
- [Performance](#performance)
- [Testing](#testing)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [Code Style](#code-style)
- [Development Guide](#development-guide)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License](#license)
- [Authors](#authors)
- [Citation](#citation)
- [Acknowledgements](#acknowledgements)

---

## Overview

### The problem

Emergency Departments are one of the most resource-constrained parts of any hospital system. Every patient who walks in needs a rapid, informed answer to one question: **will this person need to be admitted?** That decision today depends almost entirely on physician judgment, made under time pressure, with incomplete information. Meanwhile, most machine-learning attempts at this problem stop at a single accuracy number, ignore the fact that ED survey data is *sampled*, not exhaustive, and hand clinicians an unexplained probability they have no reason to trust.

### The solution

**HealthIQ** is a full-stack platform that takes a curated set of triage-time patient information — demographics, vitals, triage level, arrival method, and (optionally) early workup details — and returns, in real time:

- A calibrated **probability of hospital admission**
- A **confidence score** and a **low / moderate / high risk category**
- A **SHAP-based explanation** naming exactly which factors pushed the prediction up or down
- A plain-language summary a clinician can read without any ML background

Every prediction is persisted to a **Prediction History**, and the model's **global** behavior (which features matter most across the whole population, not just one patient) is explorable independently of any single prediction.

### The motivation

This project treats healthcare AI as a **decision-support** tool, not a replacement for clinical judgment — a distinction repeated throughout this codebase and its UI copy, not just in this README. The build was carried out sprint-by-sprint as a research-and-production exercise: a full data pipeline (NHAMCS 2022 SAS extract → cleaned, engineered, encoded, scaled dataset), a documented multi-model comparison (Logistic Regression through gradient boosting and a stacking ensemble), a survey-aware learning track that treats NHAMCS as the complex national survey it actually is (not a naive random sample), a first-class explainability layer, a versioned REST API, and a modern React dashboard — each layer independently testable and independently replaceable.

### Why explainability matters

Per this project's own engineering guide (`CLAUDE.md`): *"Every prediction must include an explanation. Explainability is a required feature. Not an optional enhancement."* The backend's `/predict` endpoint is architecturally incapable of returning a prediction without its SHAP explanation attached — there is no prediction-only response shape in the API contract.

### Why healthcare AI needs this rigor

A probability score with no explanation is not decision support — it's an unaccountable black box that a physician has every reason to distrust and ignore. HealthIQ's explanations name the *specific* clinical factors (e.g. "a requested specialist consultation increased the predicted risk the most, while advanced age decreased it") behind every number, so the output is something a clinician can actually reason about and challenge.

### Why NHAMCS

The **National Hospital Ambulatory Medical Care Survey (NHAMCS)** is a nationally representative, publicly available, de-identified U.S. government survey of Emergency Department visits — real clinical patterns, at national scale, with a rigorous sampling methodology, and no patient-privacy risk in using it for research. This project uses the **2022 Emergency Department** dataset, distributed as a SAS7BDAT file with an accompanying data dictionary.

---

## Features

| Feature | Description |
|---|---|
| 🧠 **AI-powered prediction** | Real-time admission probability from a production LightGBM model, served behind a versioned REST API |
| 🔍 **Explainable by design** | Every prediction ships with a SHAP-based breakdown — no black-box scores, ever |
| 🌍 **Global explainability** | Explore model-wide feature importance (866 engineered features, or grouped back to their clinical source variable), independent of any single prediction |
| 🎯 **Local explainability** | Per-prediction SHAP contributions (which factors increased/decreased *this* patient's risk) |
| 📊 **Interactive dashboard** | Live system/model/database health, recent predictions, and a computed risk insight, all from real data |
| 📝 **Curated clinical form** | An ~18-field patient form (not NHAMCS's ~900 raw columns) — every omitted field is safely imputed server-side |
| 🕘 **Prediction history** | Every prediction persisted and browsable, with client-side sort/filter by risk category |
| 🚦 **Risk visualization** | Diverging SHAP contribution charts (Recharts), color-coded and text-labeled for colorblind-safety |
| 📱 **Responsive UI** | Verified overflow-free at desktop, tablet, and mobile widths across every page |
| 🌗 **Dark mode** | Full light/dark theming via CSS custom properties and `next-themes` |
| ⚡ **Fast inference** | Model, preprocessing pipeline, and SHAP explainer loaded once at process startup — never per request |
| 🔬 **Survey-aware ML track** | A parallel research track evaluating cluster-robust/weighted GLMs against the naive approach, since NHAMCS is a complex survey, not a simple random sample |
| 🏗️ **Enterprise architecture** | Strict separation of concerns — ML never imports FastAPI, the backend never trains models, the frontend never computes a prediction |
| 🧪 **Research-ready** | Reproducible pipeline scripts, experiment logging, Jupyter reports, and a documented model-selection process |
| 🎨 **Modern frontend** | React 19 + Vite 8 + Tailwind v4 + shadcn/ui (Radix primitives), with a public marketing landing page separate from the authenticated-feeling app shell |

---

## Screenshots

> Screenshots are not yet checked into this repository. Add PNGs under `docs/images/` and update the paths below — the layout is ready to go.

| Page | Preview |
|---|---|
| Public landing page | `docs/images/landing.png` |
| Dashboard | `docs/images/dashboard.png` |
| Patient prediction form + result | `docs/images/prediction.png` |
| SHAP explainability | `docs/images/explainability.png` |
| Prediction history | `docs/images/history.png` |
| Dark mode | `docs/images/dark-mode.png` |

---

## Demo

> Placeholders — fill these in once available.

- **Live Demo**: _not yet deployed — see [Deployment](#deployment)_
- **Video Demo**: _not yet recorded_
- **Research Paper**: _not yet published_
- **Presentation Slides**: _not yet published_

---

## Architecture

HealthIQ is a strict three-layer, monorepo architecture. Each layer is independently testable and independently replaceable — the frontend never imports ML code, and the ML layer never imports FastAPI.

```
                         ┌─────────────────────────┐
                         │      NHAMCS Dataset      │
                         │  (Data/raw/*.sas7bdat)   │
                         └────────────┬─────────────┘
                                      │
                                      ▼
                     ┌────────────────────────────────┐
                     │   ML Data & Training Pipeline    │
                     │  ingestion → cleaning → feature  │
                     │  engineering → encoding/scaling  │
                     │  → train/test split → modeling   │
                     └────────────────┬─────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        ▼                            ▼
              ┌──────────────────┐        ┌───────────────────────┐
              │  Trained Model    │        │  Explainability Engine │
              │  (LightGBM, .pkl) │        │  (SHAP TreeExplainer)  │
              └─────────┬─────────┘        └───────────┬───────────┘
                        └───────────────┬───────────────┘
                                        ▼
                         ┌───────────────────────────┐
                         │      FastAPI Backend       │
                         │  validation → inference →  │
                         │  explanation → persistence │
                         └──────────────┬──────────────┘
                                        │  REST (JSON, /api/v1)
                                        ▼
                         ┌───────────────────────────┐
                         │   React Frontend (Vite)    │
                         │  landing → dashboard →     │
                         │  prediction → explainability│
                         │  → history → about          │
                         └──────────────┬──────────────┘
                                        ▼
                                    👤 Users
```

**Request-level flow** (a single prediction, end to end):

```
Frontend form submit
        │
        ▼
POST /api/v1/predict  (Pydantic validation, extra fields rejected)
        │
        ▼
PatientRecordAssembler   (18 curated fields → full raw NHAMCS-shaped record, rest left null)
        │
        ▼
PreprocessingPipeline.transform()   (same fitted pipeline used at training time)
        │
        ▼
LightGBM model.predict_proba()
        │
        ▼
SHAP TreeExplainer   (per-feature contribution in log-odds space)
        │
        ▼
Response assembly   (probability, confidence, risk category, top ± contributing features)
        │
        ├──▶ SQLite/PostgreSQL (prediction_history table)
        │
        ▼
JSON response → React result panel + SHAP chart
```

The backend is the **only** integration point between the ML subsystem and the frontend — the frontend calls REST endpoints exclusively, and the ML layer is called only through `ML.explainability.service` / `ML.explainability.artifacts`, never duplicated inside `Backend/`.

---

## Tech Stack

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| [React](https://react.dev) | 19.2 | UI library |
| [Vite](https://vite.dev) | 8 | Dev server & build tool |
| [React Router](https://reactrouter.com) | 7 | Client-side routing (`/` public site, `/app/*` dashboard) |
| [Tailwind CSS](https://tailwindcss.com) | v4 | Utility-first styling, CSS-variable-based theme tokens |
| [shadcn/ui](https://ui.shadcn.com) | (Radix base, "Nova" preset) | Component library — installed as owned source, not a black-box package |
| [Radix UI](https://www.radix-ui.com) | via `radix-ui` | Unstyled, accessible primitives underlying shadcn/ui |
| [Recharts](https://recharts.org) | 3 | SHAP contribution & feature-importance charts |
| [Axios](https://axios-http.com) | 1.x | HTTP client, wrapped in a single typed API client |
| [lucide-react](https://lucide.dev) | — | Icon set |
| [next-themes](https://github.com/pacocoursey/next-themes) | — | Light/dark theme switching |
| [Sonner](https://sonner.emilkowal.ski) | — | Toast notifications |
| [class-variance-authority](https://cva.style) + [tailwind-merge](https://github.com/dcastil/tailwind-merge) | — | Component variant management |
| [Geist Variable](https://vercel.com/font) | — | Typeface, self-hosted via `@fontsource-variable` |

### Backend

| Technology | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | Async REST API framework, automatic OpenAPI docs |
| [Uvicorn](https://www.uvicorn.org) (`[standard]`) | ASGI server |
| [Pydantic](https://docs.pydantic.dev) + [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Request/response validation, environment-variable settings |
| [SQLAlchemy](https://www.sqlalchemy.org) | ORM for the prediction-history table |
| [Alembic](https://alembic.sqlalchemy.org) | Database migrations |
| [SQLite](https://www.sqlite.org) (dev) / [PostgreSQL](https://www.postgresql.org) (prod-ready) | Persistence, selected entirely via `DATABASE_URL` |

### Machine Learning

| Technology | Purpose |
|---|---|
| [pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) | Data manipulation |
| [pyreadstat](https://github.com/Roche/pyreadstat) | Reading the NHAMCS `.sas7bdat` file directly |
| [scikit-learn](https://scikit-learn.org) | Preprocessing pipeline, baseline models, metrics |
| [LightGBM](https://lightgbm.readthedocs.io) | **Production model** |
| [XGBoost](https://xgboost.readthedocs.io) / [CatBoost](https://catboost.ai) | Candidate models evaluated during model selection |
| [SHAP](https://shap.readthedocs.io) | Explainability engine (TreeExplainer) — global & local, waterfall/force/decision/summary/bar/beeswarm plots |
| [statsmodels](https://www.statsmodels.org) | Survey-aware (cluster-robust / weighted) GLM comparison track |
| [joblib](https://joblib.readthedocs.io) | Model/pipeline serialization |
| [Jupyter](https://jupyter.org) | EDA, model-development, and explainability research reports |

### Developer Tools & Testing

| Technology | Purpose |
|---|---|
| [pytest](https://pytest.org) + [httpx](https://www.python-httpx.org) | Backend & ML unit/integration/API tests |
| [black](https://black.readthedocs.io) / [ruff](https://docs.astral.sh/ruff/) | Python formatting & linting |
| [Vitest](https://vitest.dev) + [React Testing Library](https://testing-library.com/react) + [jsdom](https://github.com/jsdom/jsdom) | Frontend unit/component tests |
| [oxlint](https://oxc.rs/docs/guide/usage/linter.html) | Frontend linting |

### Deployment (planned, see [Deployment](#deployment))

No Docker, CI, or hosted deployment configuration exists in this repository yet — the sections below document the recommended path, clearly marked as not-yet-implemented.

---

## Folder Structure

```
HealthIQ/
├── Backend/                     # FastAPI REST API (never trains models)
│   ├── app/
│   │   ├── api/
│   │   │   ├── health.py        # GET /health, /health/model, /health/db
│   │   │   └── v1/
│   │   │       ├── predict.py       # POST /api/v1/predict
│   │   │       ├── explain.py       # GET  /api/v1/explain/global
│   │   │       └── predictions.py   # GET  /api/v1/predictions
│   │   ├── core/                # Settings, logging, exception handlers
│   │   ├── db/                  # SQLAlchemy engine/session/base
│   │   ├── models/               # ORM models (PredictionRecord)
│   │   ├── schemas/              # Pydantic request/response contracts
│   │   ├── services/              # Business logic (never in routes)
│   │   └── main.py                # FastAPI app, CORS, lifespan model loading
│   ├── alembic/                  # Database migrations
│   ├── tests/                    # 73 pytest tests
│   └── healthiq.db               # Local SQLite database (dev default)
│
├── Frontend/                     # React + Vite SPA
│   ├── src/
│   │   ├── pages/                 # LandingPage, DashboardPage, PredictionPage,
│   │   │                          # ExplainabilityPage, PredictionHistoryPage, AboutPage
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn/ui primitives (owned source, not a package)
│   │   │   ├── forms/               # PatientRecordForm + field config/validation
│   │   │   └── charts/               # SHAP contribution & feature-importance charts
│   │   ├── layouts/                 # AppLayout (sidebar shell for /app/*)
│   │   ├── services/                 # Axios API client, one module per backend resource
│   │   ├── hooks/                    # useApiRequest (data/loading/error/execute)
│   │   └── utils/                    # formatPercentage, predictionListUtils, etc.
│   ├── public/
│   └── package.json
│
├── ML/                            # Data pipeline, training, explainability (no FastAPI import)
│   ├── ingestion/                  # Load & validate the raw SAS dataset
│   ├── eda/                        # Exploratory data analysis
│   ├── cleaning/                   # Missing values, dtypes, duplicates, sentinels
│   ├── feature_engineering/         # Encoding, scaling, derived features, selection
│   ├── pipeline/                     # PreprocessingPipeline, train/test split
│   ├── modeling/                     # Candidate models, cross-validation, tuning, stacking
│   ├── survey/                       # Survey-design diagnostics
│   ├── explainability/                # SHAP service, global/local explanations, plots
│   ├── scripts/                       # One run_*.py per pipeline stage (see Model Training)
│   ├── saved_models/                   # Production artifacts consumed by the Backend
│   ├── reports/                        # Generated markdown/CSV evaluation reports
│   ├── notebooks/                      # Jupyter research reports
│   └── tests/                          # 65 pytest tests
│
├── Data/
│   ├── raw/                       # Original NHAMCS SAS extract (untouched)
│   ├── processed/                 # Pipeline-generated train/validation/test splits (gitignored)
│   └── documents/                 # NHAMCS codebook, technical documentation
│
├── Docs/
│   └── PROJECT_CONTEXT.md          # The full product/engineering specification this project follows
│
├── CLAUDE.md                       # Engineering guide/conventions for AI-assisted contributions
├── TASKS.md                        # Living sprint-by-sprint implementation log (gitignored)
├── requirements.txt                # Python runtime dependencies (ML + Backend)
├── requirements-dev.txt            # + pytest, black, ruff, jupyter
└── .env.example                    # Backend environment variable template
```

---

## Installation

Prerequisites:

- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

Clone the repository:

```bash
git clone https://github.com/shreyes-7/HealthIQ.git
cd HealthIQ
```

The steps below are split into [Python Setup](#python-setup) (ML + Backend) and [Node Setup](#node-setup) (Frontend). Both are required to run the full application.

---

## Python Setup

Per this project's engineering guide, dependencies are installed into a `.venv` virtual environment at the repository root — never globally.

### Windows (cmd)

```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

> `requirements-dev.txt` installs `requirements.txt` (runtime: pandas, LightGBM, SHAP, FastAPI, SQLAlchemy, etc.) plus development tools (pytest, black, ruff, jupyter). Use `pip install -r requirements.txt` alone for a runtime-only install.

### Run the backend

```bash
# From the repository root, with .venv activated:
uvicorn Backend.app.main:app --reload --port 8000
```

The API is now live at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc`.

---

## Node Setup

```bash
cd Frontend
npm install
```

### Configure the environment

```bash
cp .env.example .env
# .env already defaults to VITE_API_BASE_URL=http://localhost:8000, matching the backend above
```

### Run the frontend dev server

```bash
npm run dev
```

Vite serves the app at `http://localhost:5173`.

### Build for production

```bash
npm run build      # outputs to Frontend/dist/
npm run preview    # serves the production build locally for a smoke test
```

### Lint & test

```bash
npm run lint        # oxlint
npm run test        # vitest run
```

---

## Running the Project

1. **Start the backend** (from the repo root, `.venv` activated):
   ```bash
   uvicorn Backend.app.main:app --reload --port 8000
   ```
2. **Start the frontend** (in a second terminal):
   ```bash
   cd Frontend && npm run dev
   ```
3. **Open the app**: [http://localhost:5173](http://localhost:5173) — the public landing page. Click **Launch app** to reach the dashboard at `/app`.
4. **Access the API directly**: [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger docs, or `curl http://localhost:8000/health`.
5. **Generate a prediction**: navigate to **Prediction**, fill in the required vitals/demographics/triage fields, and submit — the result panel (with its SHAP explanation) renders on the right.

The database schema is created automatically the first time the backend's test suite runs, or manually via Alembic (see [Configuration](#configuration)) — `Backend/healthiq.db` already exists in this repository for immediate local use.

---

## Model Training

The ML pipeline is a sequence of independent, reproducible scripts under `ML/scripts/`, each documenting its own invocation in its module docstring. **Run every command from the repository root**, with `.venv` activated — every script uses absolute imports (`ML.ingestion...`, `ML.modeling...`) that require the repo root on `sys.path`, which `python -m` provides automatically.

### How the dataset is processed

| Stage | Command |
|---|---|
| 1. Load & validate the raw SAS dataset | `python -m ML.scripts.run_dataset_setup` |
| 2. Exploratory data analysis | `python -m ML.scripts.run_eda` |
| 3. Data cleaning | `python -m ML.scripts.run_cleaning` |
| 4. Feature engineering | `python -m ML.scripts.run_feature_engineering` |
| 5. Train/validation/test split | `python -m ML.scripts.run_train_test_split` |
| 6. Fit & apply the preprocessing pipeline | `python -m ML.scripts.run_preprocessing_pipeline` |
| 7. Feature selection | `python -m ML.scripts.run_feature_selection` |
| 8. Survey-design diagnostics | `python -m ML.scripts.run_survey_diagnostics` |

### How the model is trained & selected

| Stage | Command |
|---|---|
| 9. Train & cross-validate every candidate model | `python -m ML.scripts.run_model_training` |
| 10. Compare candidates | `python -m ML.scripts.run_model_comparison` |
| 11. Survey-aware comparison track | `python -m ML.scripts.run_survey_aware_comparison` |
| 12. Stacking ensemble | `python -m ML.scripts.run_stacking_ensemble` |
| 13. Final model selection | `python -m ML.scripts.run_final_model_selection` |
| 14. Serialize production artifacts | `python -m ML.scripts.run_model_serialization` |

### How explainability is generated

| Stage | Command |
|---|---|
| 15. Fit the SHAP explainer | `python -m ML.scripts.run_shap_integration` |
| 16. Global explanations (feature importance) | `python -m ML.scripts.run_global_explainability` |
| 17. Local explanations (waterfall/force/decision plots) | `python -m ML.scripts.run_local_explainability` |
| 18. Readiness/reproducibility checks | `python -m ML.scripts.run_reproducibility_validation`, `run_explainability_readiness_check`, `run_backend_integration_readiness` |

### Where the model is stored

Serialized artifacts live in `ML/saved_models/`, consumed **read-only** by the Backend at startup:

```
ML/saved_models/
├── model.pkl                    # Production LightGBM model
├── preprocessing_pipeline.pkl   # Fitted preprocessing (imputation, encoding, scaling)
├── shap_explainer.pkl           # Fitted SHAP TreeExplainer
├── feature_names.json           # The 866 engineered feature names, in model order
├── model_metadata.json          # Hyperparameters, CV/validation metrics, training data reference
└── candidates/                  # Every other evaluated model (Logistic Regression, Decision Tree,
                                  # Random Forest, Gradient Boosting, XGBoost, CatBoost, Stacking Ensemble)
```

The Backend never retrains or refits anything — `ML_SAVED_MODELS_DIR` (default `ML/saved_models`) is loaded exactly once, at process startup, by `Backend.app.services.explanation_service.ExplanationRuntime`. If the artifacts are missing or incompatible, the application **refuses to start** rather than serving predictions from a broken state.

---

## Explainability

Explainability is generated entirely in the **ML layer** (`ML/explainability/`) and served by the Backend — the frontend only renders it, never computes it.

### Global SHAP (model-wide)

Computed **once**, over the validation split (not recomputed per request), and served via `GET /api/v1/explain/global`:
- **`top_features`** — mean `|SHAP|` per individual encoded feature (e.g. `CONSULT__Yes`)
- **`top_source_variables`** — the same values aggregated back to their original clinical variable (e.g. all `AGE_GROUP__*` dummies summed to `AGE_GROUP`)

The frontend's Explainability page visualizes both as horizontal bar charts, toggleable, with an adjustable `top_n` (1–866).

### Local SHAP (per-prediction)

Computed for the specific patient submitted, and returned inline with every `POST /api/v1/predict` response:
- `features_that_increased_risk` / `features_that_decreased_risk` — ranked by SHAP magnitude
- A plain-language sentence naming the single strongest factor in each direction
- Visualized as a single diverging bar chart (red = increased risk, green = decreased risk)

### Research-side visualization suite (ML layer, offline artifacts)

Beyond the lightweight JSON the live API serves, `ML/explainability/` generates the full classic SHAP visualization set as PNG research artifacts (via `run_local_explainability` / `run_global_explainability`), consumed by the Jupyter reports under `ML/notebooks/`:

| Plot type | Scope | Purpose |
|---|---|---|
| **Waterfall** | Local | Step-by-step build-up from the base rate to one patient's final prediction |
| **Force plot** | Local | Compact push/pull visualization of one prediction's contributing features |
| **Decision plot** | Local | How the prediction accumulates across features, in context of similar cases |
| **Summary plot** | Global | Per-encoded-feature SHAP value distribution across the validation set |
| **Bar plot** | Global | Mean `|SHAP|` ranking, per encoded feature |
| **Source-variable beeswarm** | Global | A custom (non-native-SHAP) beeswarm aggregated back to clinical source variables — more interpretable than a third per-encoded-feature view |

### Difference between global and local

- **Global**: "Which characteristics matter most for admission risk *in general*, across the whole validation population?" — a property of the model, not of any one patient.
- **Local**: "Why did *this specific patient's* prediction come out the way it did?" — reflects only that patient's own feature values.

---

## API Documentation

All endpoints are documented automatically via FastAPI's OpenAPI schema — visit `http://localhost:8000/docs` for the interactive, always-in-sync version. Every response (success or error) follows the same envelope: `{ status, message, data, timestamp, api_version }`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service identity/status |
| `GET` | `/health` | Liveness — confirms the process is running |
| `GET` | `/health/model` | Confirms the model, preprocessing pipeline, and SHAP explainer are loaded |
| `GET` | `/health/db` | Confirms the configured database is reachable |
| `POST` | `/api/v1/predict` | Curated patient record → admission prediction **with** its SHAP explanation |
| `GET` | `/api/v1/explain/global?top_n=20` | Precomputed global feature importance (`top_n`: 1–866) |
| `GET` | `/api/v1/predictions?limit=50` | Prediction history, most recent first (`limit`: 1–500) |

### Example: `POST /api/v1/predict`

```json
{
  "age": 67,
  "sex": 2,
  "race_ethnicity": 1,
  "pulse": 88,
  "temperature_fahrenheit": 98.6,
  "respiratory_rate": 18,
  "systolic_bp": 130,
  "diastolic_bp": 80,
  "pulse_oximetry_percent": 97,
  "triage_level": 2,
  "arrived_by_ambulance": true,
  "wait_time_minutes": 15,
  "length_of_visit_minutes": 120,
  "num_discharge_diagnoses": 3,
  "total_diagnoses": 4,
  "consult_requested": true,
  "primary_diagnosis_code": "R079",
  "num_medications": 2,
  "num_medications_given": 1
}
```

Response (`data` field, abbreviated):

```json
{
  "predicted_admission": false,
  "admission_probability": 0.109,
  "confidence_score": 0.782,
  "risk_category": "low",
  "base_rate_probability": 0.150,
  "features_that_increased_risk": [
    { "feature": "CONSULT__Yes", "source_variable": "CONSULT", "feature_value": 1.0, "shap_value": 2.64 }
  ],
  "features_that_decreased_risk": [
    { "feature": "AGE", "source_variable": "AGE", "feature_value": -0.5, "shap_value": -1.2 }
  ],
  "model_name": "lightgbm",
  "model_version": "1.0.0",
  "processing_time_ms": 1350.4
}
```

Coded fields use the raw NHAMCS codebook values (confirmed against the dataset's technical documentation, not guessed): `sex` (1=Female, 2=Male), `race_ethnicity` (1=Non-Hispanic White, 2=Non-Hispanic Black, 3=Hispanic, 4=Non-Hispanic Other), `triage_level`/IMMEDR (1=Immediate … 5=Non-urgent).

---

## Configuration

All configuration is environment-variable-driven (`Backend/app/core/config.py`, `pydantic-settings`) — nothing sensitive is hardcoded, per this project's engineering guide.

### Backend — `.env` (copy from `.env.example` at the repo root)

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `HealthIQ Backend API` | Service display name |
| `API_VERSION` | `v1` | Sets the `/api/{version}` prefix |
| `ENVIRONMENT` | `development` | Free-text environment label |
| `DEBUG` | `false` | FastAPI debug mode |
| `DATABASE_URL` | `sqlite:///./Backend/healthiq.db` | SQLAlchemy connection string — swap for a PostgreSQL URL in production |
| `ML_SAVED_MODELS_DIR` | `ML/saved_models` | Directory containing `model.pkl`, `preprocessing_pipeline.pkl`, `shap_explainer.pkl`, `feature_names.json`, `model_metadata.json` |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of origins allowed to call the API cross-origin |

### Frontend — `Frontend/.env` (copy from `Frontend/.env.example`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Base URL the Axios client targets — must match a `CORS_ALLOWED_ORIGINS` entry above |

### `.env.example` (root, Backend)

```bash
# Copy to .env and adjust for your environment. Never commit the real .env file.

APP_NAME=HealthIQ Backend API
API_VERSION=v1
ENVIRONMENT=development
DEBUG=false

# SQLAlchemy connection string. Defaults to a local SQLite file under Backend/
# for development; use a PostgreSQL URL in production, e.g.:
# postgresql+psycopg2://user:password@host:5432/healthiq
DATABASE_URL=sqlite:///./Backend/healthiq.db

# Directory containing model.pkl, preprocessing_pipeline.pkl, shap_explainer.pkl,
# feature_names.json, model_metadata.json. Defaults to ML/saved_models.
ML_SAVED_MODELS_DIR=ML/saved_models

LOG_LEVEL=INFO

# Comma-separated list of origins allowed to call this API cross-origin
# (the Frontend dev server, and later its production origin).
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### `Frontend/.env.example`

```bash
# Copy to .env and adjust for your environment.
# Must match a Backend CORS_ALLOWED_ORIGINS entry and the port this app runs on.

VITE_API_BASE_URL=http://localhost:8000
```

### Database initialization

The test suite auto-creates the schema on first run (`Backend/tests/conftest.py`). To apply migrations explicitly (e.g. against a fresh PostgreSQL instance):

```bash
# From the repository root, .venv activated:
alembic -c Backend/alembic.ini upgrade head
```

---

## Prediction Workflow

```
Patient information entered in the form
                │
                ▼
      Client-side validation
   (mirrors backend constraints —
    blocks submission before any
         network call)
                │
                ▼
     POST /api/v1/predict
   (Pydantic re-validates; extra
      fields rejected, 422 on
        invalid input)
                │
                ▼
   PatientRecordAssembler expands
   the ~18 curated fields into a
   full raw-NHAMCS-shaped record
   (everything else left null)
                │
                ▼
   PreprocessingPipeline.transform()
  (identical fitted pipeline used
     at training time — same
   median/"Missing"-category
        imputation)
                │
                ▼
       LightGBM inference
   → admission_probability
                │
                ▼
     SHAP TreeExplainer
  → per-feature contributions
       (log-odds space)
                │
                ▼
   Response assembled: probability,
  confidence, risk category, top
   increased/decreased-risk features,
      plain-language summary
                │
                ├──▶ Persisted to prediction_history
                │      (outcome + explanation reference only —
                │       never the submitted patient input)
                │
                ▼
   Rendered on the Prediction page:
  risk badge, stat tiles, SHAP chart,
        plain-language "why"
```

---

## UI Pages

| Page | Route | Description |
|---|---|---|
| **Landing** | `/` | Public marketing page — hero, live model metrics, a sample-prediction preview (the real result component, fed illustrative data), feature grid, how-it-works, tech stack, FAQ. No sidebar shell. |
| **Dashboard** | `/app` | System/model/database health at a glance, recent predictions, a computed high-risk insight from real data, and a "New Prediction" call to action. |
| **Prediction** | `/app/predict` | The curated patient-record form (Demographics / Vitals / Triage & Arrival / optional Workup details), with the result panel docked alongside it on desktop. |
| **Explainability** | `/app/explainability` | Global SHAP feature importance, by encoded feature or by source variable, with an adjustable top-N control and a real computed-on/row-count note from the live API. |
| **Prediction History** | `/app/history` | Every past prediction, with a summary stats strip (records loaded, admission rate, high-risk share) and sortable/filterable columns. |
| **About** | `/app/about` | What the platform does, how predictions/explanations work, real model performance metrics, data provenance & privacy, and stated limitations. |

There is no separate "Settings" page in the current implementation.

---

## Dataset

### NHAMCS

The **National Hospital Ambulatory Medical Care Survey**, conducted by the CDC's National Center for Health Statistics, is a nationally representative survey of Emergency Department (and outpatient) visits across the United States. This project uses the **2022 Emergency Department Patient Record** extract.

### Source

- `Data/raw/ed2022_sas.sas7bdat` — the original SAS dataset, loaded via `pyreadstat`, and **never modified in place**
- `Data/documents/` — the accompanying codebook and technical documentation (`technical Documentation.pdf`, `ed22inp.txt`, `ed22lab.txt`, `readme2022-ed-sas.txt`) used to confirm every coded-field label used in this codebase, rather than guessed

### Preprocessing

Raw survey rows (~900 columns) flow through: validation → cleaning (missing values, sentinel codes, dtype/unit correction, duplicates) → feature engineering (encoding, scaling, derived features, leakage exclusion, feature selection) → a fitted `PreprocessingPipeline` → a train/validation/test split. Every step is a separately testable, separately reproducible module under `ML/`.

### Features

**866 engineered features** feed the production model — a mix of one-hot-encoded categorical fields (e.g. `CONSULT__Yes`), frequency-encoded high-cardinality fields (e.g. `RFV53D__frequency`), and derived/numeric fields (e.g. `AGE`, `LOV`).

### Target variable

`hospital_admission` — whether the visit resulted in hospital admission (binary), sourced from the visit disposition fields per NHAMCS's own codebook, with any direct disposition leakage columns explicitly excluded from the feature set (`ML/feature_engineering/leakage_exclusion.py`).

### Research value

NHAMCS's survey design (not a simple random sample) is itself a research question here — see the **survey-aware** track under [Machine Learning](#machine-learning), which compares naive modeling against cluster-robust/weighted approaches.

### Ethics

NHAMCS is de-identified, publicly released U.S. government survey data — no real patient identities are used in training or ever exposed. Predictions submitted through this app's UI are stored (outcome + explanation reference only, never the input vitals/demographics) so they can appear in Prediction History; they are not shared outside this application.

### Limitations

The model reflects patterns in **2022 U.S. survey data** and may not generalize to every population, region, care setting, or time period. It is a research/decision-support signal, not a diagnostic device, and does not replace clinical judgment.

---

## Machine Learning

### Algorithm

**LightGBM** (gradient-boosted decision trees) was selected after a documented comparison against Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, CatBoost, and a stacking ensemble (`ML/saved_models/candidates/`).

**Selection criteria** (in order): validation **PR-AUC** (more informative than ROC-AUC at this task's ~13% positive rate) → **recall/sensitivity** (a missed admission is the costlier clinical error) → training time → interpretability.

**Hyperparameters**: `num_leaves=127`, `n_estimators=400`, `learning_rate=0.05`, `subsample=0.85`, `class_weight=balanced`, trained on 866 features.

### Cross-validation

5-fold cross-validation on the training split.

### Metrics (validation split)

| Metric | Value |
|---|---|
| ROC-AUC | **0.9649** (5-fold CV mean: 0.9518) |
| PR-AUC | **0.8275** |
| Accuracy | 0.9330 |
| Precision | 0.7716 |
| Recall / Sensitivity | 0.7013 |
| Specificity | 0.9684 |
| F1 | 0.7348 |
| Brier score | 0.0528 |

### Metrics (held-out test split — evaluated exactly once, for confirmation only)

| Metric | Value |
|---|---|
| ROC-AUC | 0.9564 |
| PR-AUC | 0.7599 |
| Accuracy | 0.9305 |
| Precision | 0.7559 |
| Recall / Sensitivity | 0.7013 |
| F1 | 0.7276 |
| Confusion matrix | TN 2014 · FP 72 · FN 95 · TP 223 |

### Calibration

Brier score of 0.0528 on validation — the model's predicted probabilities are reasonably well-calibrated, not just rank-ordered. `base_rate_probability` (the model's average predicted probability across the validation split) is returned alongside every prediction so a user can judge a given probability relative to the population baseline.

### Why this model was chosen

LightGBM offered the best PR-AUC/recall trade-off among all candidates, trains fast enough for iterative experimentation, and — critically for this project's explainability requirement — is fully compatible with SHAP's efficient, exact `TreeExplainer`, unlike some ensemble/stacking alternatives.

---

## Explainable AI

### SHAP

**SHapley Additive exPlanations** attributes each prediction to its input features using a game-theoretic (Shapley value) approach, computed here via SHAP's `TreeExplainer` — exact and efficient for tree-based models like LightGBM.

### Clinical transparency

Every prediction names the specific factors that moved it, in the same units the model reasoned in (log-odds/margin space, translated to a plain-language sentence) — a clinician can see *why*, not just *what*.

### Trustworthiness & interpretability

Explanations are generated by the ML layer using the exact fitted model and pipeline that produced the prediction — never approximated, mocked, or computed independently by the API or frontend.

### Responsible AI

Explainability is treated as a **required feature**, not an add-on: the `/predict` endpoint's response schema has no code path that omits `features_that_increased_risk`/`features_that_decreased_risk`. The product's own UI copy (landing page, About page) states plainly, in multiple places, that this is a research and decision-support tool, not a replacement for clinical judgment and not a diagnostic device.

---

## Security

- **Input validation**: every request is validated by Pydantic (`extra="forbid"` on the patient-record schema — unexpected fields are rejected, not silently ignored); out-of-range values (age, vitals, triage level) return a structured `422` before reaching the model
- **API validation**: range/type constraints are enforced on every query parameter (`top_n`: 1–866, `limit`: 1–500)
- **Error handling**: categorized exception handlers (`Backend/app/core/exceptions.py`) return a consistent `ErrorResponse` envelope — no stack traces, file paths, or internal exception messages ever reach the client
- **Environment variables**: all configuration (database URL, model path, CORS origins) is sourced from `Settings` (pydantic-settings) — nothing sensitive is hardcoded, and `.env` is gitignored
- **Model protection**: the backend only ever *reads* serialized model artifacts; there is no code path that retrains, refits, or otherwise mutates them at runtime
- **Sensitive data**: prediction logs and the `prediction_history` table deliberately exclude the patient's submitted input (age/vitals/demographics) — only the outcome and a small explanation reference are persisted
- **CORS**: explicit allow-list (`CORS_ALLOWED_ORIGINS`), not a wildcard

---

## Performance

- **Fast inference**: the LightGBM model, preprocessing pipeline, and SHAP explainer are loaded exactly **once**, at process startup (`lifespan` context in `Backend/app/main.py`) — never reloaded per request
- **Lazy loading**: the frontend code-splits every route beyond the landing page and dashboard (`React.lazy`), keeping Recharts (a large dependency) out of the initial bundle entirely
- **Caching**: `Settings` is `@lru_cache`d so environment variables are parsed once per process, not per request
- **Efficient preprocessing**: inference reuses the exact same fitted `PreprocessingPipeline` object from training — no re-fitting, no redundant computation
- **Known finding**: prediction+explanation latency was measured at ~2.3–2.6s per request during backend development (`Backend/reports/backend_readiness_report.md`) — workable for interactive single-patient use, but flagged as a candidate for future profiling (`PreprocessingPipeline.transform()` and `TreeExplainer` calls) if higher request volume becomes a requirement

---

## Testing

| Suite | Command | Tests |
|---|---|---|
| Backend | `python -m pytest Backend/tests/ -v` | **73 passing** |
| Machine Learning | `python -m pytest ML/tests/ -v` | **65 passing** |
| Frontend | `cd Frontend && npm run test` | **79 passing** |

**217 tests total.** Coverage includes: configuration defaults/overrides, the ML service layer, request schema validation, the patient-record assembler, every API endpoint (`TestClient`), database persistence, health checks (including simulated model/database unavailability), error-envelope consistency, logging (verifying patient data is never logged), the full data-cleaning/feature-engineering/preprocessing pipeline, cross-validation and metrics utilities, survey-aware modeling, and every frontend page/component/service/hook/utility.

Run everything:

```bash
# From the repo root, .venv activated
python -m pytest Backend/tests/ ML/tests/ -v

# Frontend, separately
cd Frontend && npm run test
```

---

## Future Improvements

- [ ] Authentication & role-based access (clinician / researcher / admin) — architecture is already layered to support this without redesign
- [ ] Hospital system integration (FHIR / HL7)
- [ ] Multi-model support in production (serve/compare more than one active model)
- [ ] Real-time model/data drift monitoring
- [ ] Cloud deployment (containerization, managed Postgres)
- [ ] Doctor portal / patient portal role separation
- [ ] Batch prediction (CSV upload → bulk results)
- [ ] PDF report export for a single prediction
- [ ] Automated model retraining pipeline
- [ ] Bias/fairness auditing dashboard (an initial fairness-audit script already exists in `ML/scripts/run_fairness_audit.py` as a research artifact)
- [ ] CI pipeline (lint + test on every PR)

---

## Contributing

1. **Fork** the repository
2. **Branch** from `main`: `git checkout -b feature/your-feature-name`
3. **Commit** with a clear, conventional message (see [Code Style](#code-style)): `git commit -m "feat: add X"`
4. **Push** to your fork: `git push origin feature/your-feature-name`
5. **Open a Pull Request** against `main`, describing what changed and why

Before opening a PR, make sure it:

- Compiles/builds successfully (`npm run build` for the frontend)
- Passes the relevant test suite(s) (see [Testing](#testing))
- Follows the existing architecture — ML never imports FastAPI, the backend never trains models, the frontend never computes a prediction
- Avoids unrelated changes — keep PRs focused

---

## Code Style

- **Python**: formatted with `black`, linted with `ruff` (both in `requirements-dev.txt`)
- **JavaScript/JSX**: linted with `oxlint` (`Frontend/.oxlintrc.json`); no separate formatter is currently configured
- **Naming**: descriptive, unabbreviated names throughout (`admission_probability`, not `adm_prob`)
- **Commit messages**: conventional prefixes — `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- **Folder organization**: one responsibility per file (`prediction_service.py` only contains prediction logic, `router.py` files contain routes and nothing else); shared logic is extracted into reusable modules rather than duplicated

---

## Development Guide

### Component architecture (Frontend)

- `src/components/ui/` — shadcn/ui primitives, owned as source code, styled via Tailwind semantic tokens only (`bg-primary`, `text-muted-foreground` — never raw hex values)
- `src/components/` — domain components (`RiskBadge`, `StatTile`, `PredictionResult`, `PageHeader`, …), composed from `ui/` primitives
- `src/pages/` — one file per route, composing domain components; pages never contain business logic, only presentation and API calls via `useApiRequest`

### API structure (Backend)

Every endpoint follows the same layering: **route → validate (Pydantic) → service → response**. Routes never contain business logic; services never import FastAPI types.

### ML pipeline

Each pipeline stage (`ML/ingestion`, `ML/cleaning`, `ML/feature_engineering`, `ML/modeling`, `ML/explainability`) is an independent, independently-tested Python package. Add a new model by registering it in `ML/modeling/model_registry.py` — no changes to the Backend are required until you're ready to promote it to production (`run_model_serialization.py`).

### Best practices

- Never hardcode configuration — extend `Backend/app/core/config.py`'s `Settings` class and `.env.example`
- Never duplicate a utility — check `src/utils/` (frontend) or the relevant `ML/` subpackage before writing a new one
- Every new page/component/service gets a corresponding test file alongside it

---

## Deployment

No Docker, CI, or hosted deployment configuration exists in this repository yet. The guidance below is a recommended path, not a description of existing infrastructure.

### Docker (recommended first step, not yet implemented)

A minimal setup would containerize the Backend (`uvicorn Backend.app.main:app`) and Frontend (`vite build` output served via Nginx or a static host) as two services, with `DATABASE_URL` pointed at a managed Postgres instance instead of local SQLite.

### Backend hosting (Render / Railway / AWS / Azure / DigitalOcean)

Any platform that can run a long-lived Python process works: install `requirements.txt`, set the environment variables from [Configuration](#configuration) (in particular `DATABASE_URL` and `CORS_ALLOWED_ORIGINS` pointed at your deployed frontend origin), and run `uvicorn Backend.app.main:app --host 0.0.0.0 --port $PORT`. Ensure `ML/saved_models/` (or an equivalent `ML_SAVED_MODELS_DIR`) is present in the deployed environment — the app refuses to start without it.

### Frontend hosting (Vercel / Netlify / static hosting)

`npm run build` produces a static `Frontend/dist/` bundle deployable to any static host. Set `VITE_API_BASE_URL` at build time to your deployed backend's URL.

### Database

SQLite (the local default) is fine for a demo; for anything persistent or multi-instance, point `DATABASE_URL` at a managed PostgreSQL instance and run `alembic -c Backend/alembic.ini upgrade head` once against it.

---

## Troubleshooting

| Problem | Likely cause / fix |
|---|---|
| `Port already in use` (8000 or 5173) | Another process is bound to the port — stop it, or run `uvicorn ... --port 8001` / edit `Frontend/vite.config.js`'s `server.port` |
| `ModuleNotFoundError: No module named 'Backend'` | You ran a command from inside `Backend/` or `ML/` — every Python command in this project must run from the **repository root** (absolute imports like `Backend.app...` require it) |
| `Missing dependencies` (Python) | Re-run `pip install -r requirements-dev.txt` inside the activated `.venv` |
| Virtual environment issues (`.venv` not activating) | On Windows, PowerShell may block script execution — run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use `.venv\Scripts\activate.bat` in cmd instead |
| Wrong Node version | This project uses Vite 8 + React 19; Node 18+ is required — check with `node --version` |
| Wrong Python version | Python 3.11+ is required (match type hints like `int \| None` used throughout the schemas) |
| `The prediction model has not finished loading` (503) | `ML_SAVED_MODELS_DIR` doesn't point at a valid artifact set, or the backend is still starting — check the startup logs for `Model loaded: name=... version=...` |
| SHAP import errors | SHAP has native/compiled dependencies — ensure you're inside the `.venv` with `requirements.txt` fully installed, and that your Python version matches a SHAP-supported build |
| Database errors (`The database is not reachable`) | Confirm `DATABASE_URL` is correct and, for SQLite, that the `Backend/` directory is writable; for Postgres, confirm the server is running and migrations have been applied |
| CORS errors in the browser console | The frontend's origin (default `http://localhost:5173`) must be listed in the backend's `CORS_ALLOWED_ORIGINS` |
| Frontend shows a blank page / 404 on `/app/*` after a hard refresh | The SPA needs history-mode fallback routing configured on whatever static host you deploy to (serve `index.html` for unmatched paths) |

---

## FAQ

**How do I train the model?**
See [Model Training](#model-training) — run the numbered `python -m ML.scripts.run_*` sequence from the repository root.

**How do I run the frontend?**
`cd Frontend && npm install && npm run dev` — see [Node Setup](#node-setup).

**How do I run the backend?**
`uvicorn Backend.app.main:app --reload --port 8000` from the repo root, with `.venv` activated — see [Python Setup](#python-setup).

**Where is the model stored?**
`ML/saved_models/model.pkl` (plus its preprocessing pipeline and SHAP explainer alongside it) — see [Model Training](#model-training).

**How do I add a new page to the frontend?**
Add a file under `Frontend/src/pages/`, register its route in `Frontend/src/App.jsx`, and add a link in `Frontend/src/components/AppSidebar.jsx` if it belongs in the app shell.

**How do I add a new API endpoint?**
Add a route module under `Backend/app/api/v1/`, a Pydantic schema under `Backend/app/schemas/`, and business logic in `Backend/app/services/` — routes should never contain logic themselves. Register the router in `Backend/app/api/v1/__init__.py`.

**How do I deploy this?**
See [Deployment](#deployment) — no hosted deployment exists yet; that section documents the recommended path.

**Is this used for real clinical decisions?**
No. HealthIQ is a research and decision-support tool. It is intended to support clinical judgment, not replace it, and it is not a diagnostic device.

---

## License

This project is licensed under the **MIT License** — see [`LICENSE`](./LICENSE).

> A `LICENSE` file has been added at the repository root with a placeholder copyright holder. Update the copyright line with the actual rights holder before distributing this project publicly.

---

## Authors

> Placeholder — replace with real contributor details.

| Role | Name | GitHub | Email |
|---|---|---|---|
| Author / Maintainer | _Your Name_ | [@shreyes-7](https://github.com/shreyes-7) | `you@example.com` |
| Contributor | _Name_ | `@github-handle` | `email@example.com` |
| Supervisor / Advisor | _Name_ (if applicable) | — | — |
| Institution | _Institution name_ (if applicable) | — | — |

---

## Citation

If you use this project or its methodology in academic work, please cite it:

```bibtex
@software{healthiq2026,
  author  = {HealthIQ Contributors},
  title   = {HealthIQ: Survey-Aware Explainable AI for Emergency Department Admission Prediction},
  year    = {2026},
  url     = {https://github.com/shreyes-7/HealthIQ},
  note    = {NHAMCS-based Emergency Department admission risk prediction with SHAP explainability}
}
```

---

## Acknowledgements

- **[CDC / NCHS](https://www.cdc.gov/nchs/ahcd/index.htm)** — for publishing the NHAMCS dataset this project is built on
- **[NHAMCS](https://www.cdc.gov/nchs/ahcd/index.htm)** — the National Hospital Ambulatory Medical Care Survey
- **[SHAP](https://shap.readthedocs.io)** — for making rigorous, game-theoretically grounded explainability practical
- **[LightGBM](https://lightgbm.readthedocs.io)** — the production model's training framework
- **[scikit-learn](https://scikit-learn.org)** — preprocessing, baseline models, and evaluation metrics throughout
- **[FastAPI](https://fastapi.tiangolo.com)** and **[React](https://react.dev)** — for making a production-quality full-stack build tractable
- **[shadcn/ui](https://ui.shadcn.com)** and the **Radix UI** team — for an accessible, ownable component foundation
- The **open source community** whose libraries make a project of this scope possible for a small team

---

<div align="center">

**HealthIQ** — explainable Emergency Department admission risk prediction, built on real data, explained by design.

*A research and decision-support tool — not a diagnostic device.*

</div>
