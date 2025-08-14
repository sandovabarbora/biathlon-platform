"""Athlete schemas for API validation"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr, Field, validator

from app.schemas.base import BaseSchema, TimestampSchema


class AthleteBase(BaseSchema):
    """Base athlete schema"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    weight: float = Field(..., gt=40, lt=150)
    height: float = Field(..., gt=140, lt=230)
    hr_max: int = Field(..., ge=120, le=220)
    vo2max: float = Field(..., ge=30, le=100)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    team: Optional[str] = None
    coach: Optional[str] = None


class AthleteCreate(AthleteBase):
    """Create athlete request"""
    pass


class AthleteUpdate(BaseSchema):
    """Update athlete request"""
    name: Optional[str] = None
    weight: Optional[float] = None
    hr_max: Optional[int] = None
    vo2max: Optional[float] = None
    lactate_threshold_1_hr: Optional[int] = None
    lactate_threshold_2_hr: Optional[int] = None
    prone_accuracy_baseline: Optional[float] = None
    standing_accuracy_baseline: Optional[float] = None


class AthleteCalibration(BaseSchema):
    """Calibration data for athlete"""
    lactate_curve: Dict[float, float]  # {hr: lactate}
    eeg_baseline_theta: float
    eeg_baseline_alpha: float
    ftp: Optional[float] = None
    max_skiing_speed: Optional[float] = None


class AthleteResponse(AthleteBase, TimestampSchema):
    """Athlete response with all fields"""
    id: int
    age: int
    hr_zones: Dict[str, tuple]
    lactate_threshold_1_hr: Optional[int] = None
    lactate_threshold_2_hr: Optional[int] = None
    prone_accuracy_baseline: float
    standing_accuracy_baseline: float
    is_active: bool


class AthleteList(BaseSchema):
    """List of athletes"""
    athletes: List[AthleteResponse]
    total: int
