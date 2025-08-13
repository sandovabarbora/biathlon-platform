"""Main FastAPI application with all endpoints"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.endpoints import athletes, analytics, races

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🎿 Starting {settings.app_name} v{settings.version}")
    logger.info("📡 Connected to IBU API via biathlonresults")
    logger.info("🇨🇿 Czech team focus enabled")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Professional Biathlon Analytics with live IBU data - Czech Team Focus",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(athletes.router, prefix="/api/v1/athletes", tags=["athletes"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(races.router, prefix="/api/v1/races", tags=["races"])

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "data_source": "Live IBU API via biathlonresults",
        "focus": "Czech National Team",
        "endpoints": {
            "athletes": "/api/v1/athletes",
            "analytics": "/api/v1/analytics",
            "races": "/api/v1/races",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "api": "connected",
        "ready": True
    }

@app.get("/api/v1/status")
async def api_status():
    """Get API status and available endpoints"""
    from app.services.ibu_full_service import ibu_service
    
    # Try to get some Czech athletes to verify connection
    czech_athletes = ibu_service.get_athletes(nation="CZE", limit=5)
    
    return {
        "status": "operational",
        "connection": "active" if czech_athletes else "limited",
        "czech_athletes_found": len(czech_athletes),
        "current_season": ibu_service.current_season,
        "available_endpoints": [
            "GET /api/v1/athletes",
            "GET /api/v1/athletes/{id}/performance",
            "GET /api/v1/athletes/{id}/history",
            "GET /api/v1/analytics/training/{id}",
            "GET /api/v1/analytics/head-to-head",
            "GET /api/v1/races",
            "GET /api/v1/races/{id}/analysis"
        ]
    }

# Add test endpoints
from app.api.endpoints import test_api
app.include_router(test_api.router, prefix="/api/v1/test", tags=["testing"])

# Add races router
from app.api.endpoints import races
app.include_router(races.router, prefix="/api/v1/races", tags=["races"])

# Test endpoints
from app.api.endpoints import test
app.include_router(test.router, prefix="/api/v1/test", tags=["test"])
