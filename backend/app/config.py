"""Application configuration with Pydantic"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # App
    app_name: str = "Biathlon Analytics"
    version: str = "1.0.0"
    debug: bool = True
    
    # API
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite:///./biathlon.db"
    
    # CORS
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
