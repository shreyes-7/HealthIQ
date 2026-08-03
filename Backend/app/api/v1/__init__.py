from fastapi import APIRouter

from Backend.app.api.v1.explain import router as explain_router
from Backend.app.api.v1.predict import router as predict_router
from Backend.app.api.v1.predictions import router as predictions_router

api_router = APIRouter()
api_router.include_router(predict_router)
api_router.include_router(explain_router)
api_router.include_router(predictions_router)
