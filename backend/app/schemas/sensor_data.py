"""Sensor data schemas"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import Field, validator

from app.schemas.base import BaseSchema


class SensorDataBase(BaseSchema):
    """Base sensor data"""
    timestamp: datetime
    heart_rate: Optional[float] = Field(None, ge=30, le=250)
    respiratory_rate: Optional[float] = Field(None, ge=5, le=60)
    core_temperature: Optional[float] = Field(None, ge=35, le=42)
    activity_type: Optional[str] = None
    
    @validator("activity_type")
    def validate_activity(cls, v):
        if v and v not in ["skiing", "shooting", "rest", "transition"]:
            raise ValueError("Invalid activity type")
        return v


class SensorDataCreate(SensorDataBase):
    """Create sensor data request"""
    heart_rate_variability: Optional[Dict[str, float]] = None
    imu_raw: Optional[List[float]] = None
    ecg_raw: Optional[List[float]] = None
    
    # Environmental
    altitude: Optional[float] = None
    temperature: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None


class IMUData(BaseSchema):
    """IMU sensor data"""
    timestamp: datetime
    acceleration: List[float] = Field(..., min_items=3, max_items=3)
    angular_velocity: List[float] = Field(..., min_items=3, max_items=3)
    magnetometer: Optional[List[float]] = Field(None, min_items=3, max_items=3)


class SensorDataResponse(SensorDataBase):
    """Sensor data response"""
    id: str
    athlete_id: int
    lactate_estimated: Optional[float] = None
    lactate_confidence: Optional[float] = None
    body_sway_ap: Optional[float] = None
    body_sway_ml: Optional[float] = None
    rifle_sway_horizontal: Optional[float] = None
    rifle_sway_vertical: Optional[float] = None


class RealtimeData(BaseSchema):
    """Real-time sensor data for WebSocket"""
    timestamp: datetime
    heart_rate: float
    heart_rate_zone: str
    lactate_estimated: float
    activity_type: str
    fatigue_index: float
    readiness_score: float
