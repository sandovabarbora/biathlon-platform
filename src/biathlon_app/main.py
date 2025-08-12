"""
Biathlon Pro - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from biathlon_app.api import routes
from biathlon_app.data import loader
from biathlon_app.utils import config

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🎿 Starting Biathlon Pro...")
    # Load data on startup
    loader.load_all_data()
    yield
    logger.info("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Biathlon Pro",
    description="Professional Analytics Platform for Biathlon Coaches",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Biathlon Pro",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "biathlon_app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )
