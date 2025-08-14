"""Athlete model with physiological parameters"""
from sqlalchemy import Column, String, Float, Integer, JSON, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import BaseModel


class Athlete(Base, BaseModel):
    """Athlete with calibrated physiological parameters"""
    __tablename__ = "athletes"
    
    # Basic info
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))  # male/female
    
    # Physical characteristics
    weight = Column(Float, nullable=False)  # kg
    height = Column(Float, nullable=False)  # cm
    
    # Physiological parameters
    hr_max = Column(Integer, nullable=False)
    hr_rest = Column(Integer)
    vo2max = Column(Float, nullable=False)
    
    # Lactate thresholds (individualized)
    lactate_threshold_1_hr = Column(Integer)  # HR at LT1
    lactate_threshold_2_hr = Column(Integer)  # HR at LT2
    lactate_curve = Column(JSON)  # Full lactate curve data
    
    # Performance benchmarks
    ftp = Column(Float)  # Functional Threshold Power (watts)
    max_skiing_speed = Column(Float)  # km/h
    
    # Shooting performance baseline
    prone_accuracy_baseline = Column(Float, default=0.85)
    standing_accuracy_baseline = Column(Float, default=0.75)
    
    # Training info
    experience_years = Column(Integer)
    team = Column(String(100))
    coach = Column(String(100))
    
    # EEG baseline patterns (for psychological model)
    eeg_baseline_theta = Column(Float)
    eeg_baseline_alpha = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sensor_data = relationship("SensorData", back_populates="athlete", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="athlete", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="athlete", cascade="all, delete-orphan")
    
    @property
    def age(self) -> int:
        """Calculate age from date of birth"""
        from datetime import datetime
        if self.date_of_birth:
            return (datetime.utcnow() - self.date_of_birth).days // 365
        return 25  # Default age
    
    @property
    def hr_zones(self) -> dict:
        """Calculate HR training zones"""
        return {
            "recovery": (0.5 * self.hr_max, 0.6 * self.hr_max),
            "aerobic": (0.6 * self.hr_max, 0.75 * self.hr_max),
            "threshold": (0.75 * self.hr_max, 0.87 * self.hr_max),
            "vo2max": (0.87 * self.hr_max, 0.95 * self.hr_max),
            "neuromuscular": (0.95 * self.hr_max, self.hr_max)
        }
