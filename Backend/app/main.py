"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Backend.app.api.health import router as health_router
from Backend.app.api.v1 import api_router
from Backend.app.core.config import get_settings
from Backend.app.core.exceptions import register_exception_handlers
from Backend.app.core.logging import configure_logging, get_logger
from Backend.app.services.explanation_service import ExplanationRuntime

settings = get_settings()
configure_logging(settings)
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Loads the model, preprocessing pipeline, and SHAP explainer once,
    at startup -- never per request. If artifacts are missing or
    incompatible, this raises and the application refuses to start rather
    than serving predictions from a broken state."""
    logger.info("Application startup: environment=%s", settings.environment)

    app.state.explanation_runtime = ExplanationRuntime()
    logger.info(
        "Model loaded: name=%s version=%s",
        app.state.explanation_runtime.model_name,
        app.state.explanation_runtime.model_version,
    )

    yield

    logger.info("Application shutdown")


app = FastAPI(
    title=settings.app_name,
    description="Emergency Department admission prediction and explainability API.",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan,
)


register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
def read_root() -> dict:
    return {"service": settings.app_name, "status": "running", "environment": settings.environment}
