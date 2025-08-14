"""Application configuration using Pydantic Settings"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Biathlon Digital Twin"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://biathlon:biathlon123@localhost:5432/biathlon_dt"
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # ML Models
    MODEL_PATH: str = "./models"
    MODEL_VERSION: str = "v1.0.0"
    
    # Sensor Configuration (Hz)
    IMU_SAMPLING_RATE: int = 200
    ECG_SAMPLING_RATE: int = 256
    
    # Physiological Constants (from research)
    HR_MAX_FORMULA: str = "220-age"  # or "Tanaka"
    LACTATE_THRESHOLD_1: float = 2.0  # mmol/L
    LACTATE_THRESHOLD_2: float = 4.0  # mmol/L
    
    # Biomechanical Thresholds
    RIFLE_SWAY_THRESHOLD_ELITE: float = 0.55  # mm/s
    POSTURAL_SWAY_RECOVERY_TIME: int = 300  # seconds
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
