"""API router configuration"""

from fastapi import APIRouter
from app.api.endpoints import athletes, analytics, races

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
