"""Training session model"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class TrainingSession(Base):
    """Training session with summary metrics"""
    __tablename__ = "training_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    
    # Session info
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Float)
    
    # Type and intensity
    session_type = Column(String(50))  # endurance, intervals, shooting, combined
    planned_intensity = Column(String(20))  # easy, moderate, hard, max
    
    # Summary metrics
    distance_km = Column(Float)
    elevation_gain_m = Column(Float)
    average_speed_kmh = Column(Float)
    
    # Physiological summary
    average_hr = Column(Float)
    max_hr = Column(Float)
    time_in_zones = Column(JSON)  # {zone: minutes}
    training_load = Column(Float)  # TRIMP score
    
    # Shooting summary (if applicable)
    total_shots = Column(Integer)
    hits = Column(Integer)
    shooting_accuracy = Column(Float)
    average_shooting_time = Column(Float)
    
    # Subjective metrics
    rpe = Column(Integer)  # Rate of Perceived Exertion (1-10)
    notes = Column(Text)
    
    # Weather conditions
    weather_conditions = Column(JSON)
    
    # Relationships
    athlete = relationship("Athlete", back_populates="training_sessions")
