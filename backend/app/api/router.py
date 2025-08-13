"""API router configuration"""

from fastapi import APIRouter
from app.api.endpoints import athletes, analytics, races, fatigue, shooting_patterns

api_router = APIRouter()

api_router.include_router(
    athletes.router,
    prefix="/athletes",
    tags=["athletes"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

api_router.include_router(
    races.router,
    prefix="/races",
    tags=["races"]
)

api_router.include_router(
    fatigue.router,
    prefix="/fatigue",
    tags=["fatigue"]
)

api_router.include_router(
    shooting_patterns.router,
    prefix="/shooting",
    tags=["shooting"]
)
