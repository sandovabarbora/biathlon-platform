"""Prediction and recommendation model"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Prediction(Base):
    """ML predictions with confidence and validation"""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    
    # Prediction type and context
    prediction_type = Column(String(50), nullable=False)  # shooting, lactate, fatigue, approach
    race_type = Column(String(50))  # sprint, individual, pursuit, mass_start
    bout_number = Column(Integer)  # 1-5 for shooting
    
    # Predicted values
    predicted_value = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    confidence_score = Column(Float)  # 0-1
    
    # Actual values (for validation)
    actual_value = Column(Float)
    error = Column(Float)  # predicted - actual
    
    # Contributing factors
    contributing_factors = Column(JSON)  # {factor: weight}
    feature_importance = Column(JSON)
    
    # Recommendations
    recommendations = Column(JSON)  # List of actionable recommendations
    priority = Column(String(20))  # low, medium, high, critical
    
    # Model metadata
    model_name = Column(String(100))
    model_version = Column(String(50))
    model_confidence = Column(Float)
    
    # Validation
    was_followed = Column(Boolean)  # Were recommendations followed?
    outcome_quality = Column(Float)  # 0-1 rating of outcome
    
    # Relationships
    athlete = relationship("Athlete", back_populates="predictions")
