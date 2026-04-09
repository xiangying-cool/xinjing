from fastapi import APIRouter

from app.api.api_v1.endpoints.auth import router as auth_router
from app.api.api_v1.endpoints.chat import router as chat_router
from app.api.api_v1.endpoints.depression_predict import router as depression_predict_router
from app.api.api_v1.endpoints.evaluations import router as evaluations_router
from app.api.api_v1.endpoints.health import router as health_router
from app.api.api_v1.endpoints.mood import router as mood_router
from app.api.api_v1.endpoints.reports import router as reports_router
from app.api.api_v1.endpoints.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(evaluations_router)
api_router.include_router(reports_router)
api_router.include_router(mood_router)
api_router.include_router(chat_router)
api_router.include_router(depression_predict_router)
