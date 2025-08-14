"""Main API router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    athletes,
    sensors,
    predictions,
    websocket,
    training
)

api_router = APIRouter()

# Include routers
api_router.include_router(
    athletes.router,
    prefix="/athletes",
    tags=["athletes"]
)

api_router.include_router(
    sensors.router,
    prefix="/sensors",
    tags=["sensors"]
)

api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["predictions"]
)

api_router.include_router(
    training.router,
    prefix="/training",
    tags=["training"]
)

api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["websocket"]
)
