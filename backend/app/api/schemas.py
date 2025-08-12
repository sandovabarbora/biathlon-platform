"""Pydantic schemas for API validation"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class RaceType(str, Enum):
    SPRINT = "Sprint"
    PURSUIT = "Pursuit"
    INDIVIDUAL = "Individual"
    MASS_START = "Mass Start"
    RELAY = "Relay"

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

# Athlete schemas
class AthleteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    nation: str = Field(..., min_length=3, max_length=3)
    birth_date: Optional[datetime] = None
    ibu_id: Optional[str] = None
    active: bool = True

class AthleteCreate(AthleteBase):
    pass

class AthleteUpdate(BaseModel):
    name: Optional[str] = None
    nation: Optional[str] = None
    active: Optional[bool] = None

class AthleteResponse(AthleteBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Performance schemas
class ShootingStats(BaseModel):
    total_accuracy: float = Field(..., ge=0, le=100)
    prone_accuracy: float = Field(..., ge=0, le=100)
    standing_accuracy: float = Field(..., ge=0, le=100)
    avg_shooting_time: Optional[float] = None

class PerformanceStats(BaseModel):
    athlete_id: int
    total_races: int = Field(..., ge=0)
    avg_rank: float = Field(..., ge=1)
    median_rank: float = Field(..., ge=1)
    best_rank: int = Field(..., ge=1)
    worst_rank: int = Field(..., ge=1)
    shooting: ShootingStats
    avg_ski_time: float = Field(..., ge=0)
    consistency_score: float = Field(..., ge=0, le=100)
    recent_form: float = Field(..., ge=-100, le=100)
    points_total: int = Field(..., ge=0)

# Race schemas
class RaceBase(BaseModel):
    date: datetime
    location: str
    event_type: RaceType
    gender: str = Field(..., pattern="^[MW]$")
    distance: float = Field(..., gt=0)

class RaceCreate(RaceBase):
    pass

class RaceResponse(RaceBase):
    id: int
    total_athletes: Optional[int] = 0
    
    model_config = ConfigDict(from_attributes=True)

# Race result schemas
class RaceResultBase(BaseModel):
    rank: int = Field(..., ge=1)
    bib: int = Field(..., ge=1)
    shooting_total: int = Field(..., ge=0, le=20)
    shooting_prone: str
    shooting_standing: str
    ski_time: float = Field(..., ge=0)
    total_time: float = Field(..., ge=0)
    time_behind: float = Field(..., ge=0)

class RaceResultCreate(RaceResultBase):
    athlete_id: int
    race_id: int

class RaceResultResponse(RaceResultBase):
    id: int
    athlete: AthleteResponse
    
    model_config = ConfigDict(from_attributes=True)

# Analytics schemas
class TrainingRecommendation(BaseModel):
    priority: Priority
    area: str
    description: str
    expected_impact: str
    exercises: List[str] = Field(..., min_length=1)
    metrics_to_track: List[str] = []

class ComparisonResult(BaseModel):
    athlete1: AthleteResponse
    athlete2: AthleteResponse
    better_shooting: str
    better_skiing: str
    better_consistency: str
    head_to_head_wins: dict
