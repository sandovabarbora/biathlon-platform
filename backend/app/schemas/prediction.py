"""Prediction schemas"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import Field

from app.schemas.base import BaseSchema


class PredictionBase(BaseSchema):
    """Base prediction schema"""
    prediction_type: str
    predicted_value: float
    confidence_score: float = Field(..., ge=0, le=1)


class ShootingPredictionRequest(BaseSchema):
    """Request for shooting prediction"""
    position: str = Field(..., pattern="^(prone|standing)$")
    bout_number: int = Field(..., ge=1, le=5)
    current_heart_rate: float = Field(..., ge=60, le=220)
    current_lactate: Optional[float] = None
    wind_speed: float = Field(default=0, ge=0, le=20)
    wind_direction: float = Field(default=0, ge=0, le=360)
    temperature: float = Field(default=0, ge=-30, le=40)


class ShootingPredictionResponse(PredictionBase):
    """Shooting prediction response"""
    timestamp: datetime
    position: str
    bout_number: int
    predicted_accuracy: float = Field(..., ge=0, le=1)
    expected_hits: int = Field(..., ge=0, le=5)
    confidence_interval: tuple[float, float]
    
    # Factors
    contributing_factors: Dict[str, float]
    
    # Recommendations
    recommendations: List[str]
    optimal_timing: Optional[float] = None  # Seconds to wait
    
    # Risk assessment
    miss_probability: float
    critical_factors: List[str]


class ApproachOptimizationRequest(BaseSchema):
    """Request for approach optimization"""
    distance_to_range: float = Field(..., gt=0, le=2000)
    current_speed: float = Field(..., gt=0, le=15)
    current_heart_rate: float = Field(..., ge=60, le=220)
    current_lactate: Optional[float] = None
    terrain: str = Field(default="flat", pattern="^(uphill|downhill|flat)$")


class ApproachOptimizationResponse(BaseSchema):
    """Optimized approach strategy"""
    timestamp: datetime
    current_hr: float
    predicted_hr_arrival: float
    target_hr: float
    optimal_hr_range: tuple[float, float]
    
    # Speed recommendations
    recommended_speed_profile: List[Dict[str, float]]  # [{distance: speed}]
    deceleration_point: float
    estimated_time_to_range: float
    
    # Recovery
    estimated_recovery_time: float
    recovery_breathing_pattern: str
    
    # Tactical advice
    energy_cost: float
    fatigue_impact: float
    recommendations: List[str]


class FatigueAssessment(BaseSchema):
    """Fatigue and readiness assessment"""
    timestamp: datetime
    fatigue_index: float = Field(..., ge=0, le=1)
    recovery_status: float = Field(..., ge=0, le=1)
    readiness_score: float = Field(..., ge=0, le=1)
    
    # Components
    muscular_fatigue: float
    neural_fatigue: float
    metabolic_stress: float
    
    # Recommendations
    training_readiness: str  # green, yellow, red
    recommended_intensity: str
    recovery_actions: List[str]
