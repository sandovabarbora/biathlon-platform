"""Sensor data time-series model"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SensorData(Base):
    """Time-series sensor data with TimescaleDB optimization"""
    __tablename__ = "sensor_data"
    
    # Primary key for time-series
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    athlete_id = Column(Integer, ForeignKey("athletes.id"), nullable=False)
    
    # Physiological data
    heart_rate = Column(Float)
    heart_rate_variability = Column(JSON)  # {rMSSD, pNN50, SDNN, HF, LF}
    respiratory_rate = Column(Float)
    core_temperature = Column(Float)
    spo2 = Column(Float)  # Blood oxygen saturation
    
    # Estimated metabolic data
    lactate_estimated = Column(Float)
    lactate_confidence = Column(Float)
    vo2_estimated = Column(Float)
    energy_expenditure = Column(Float)  # kcal/min
    
    # IMU data (aggregated)
    acceleration_magnitude = Column(Float)
    angular_velocity_magnitude = Column(Float)
    body_sway_ap = Column(Float)  # Anteroposterior sway
    body_sway_ml = Column(Float)  # Mediolateral sway
    
    # Rifle stability (when shooting)
    rifle_sway_horizontal = Column(Float)
    rifle_sway_vertical = Column(Float)
    trigger_pressure = Column(Float)
    
    # Raw sensor arrays (JSON for flexibility)
    imu_raw = Column(JSON)  # 9-axis IMU data array
    ecg_raw = Column(JSON)  # ECG waveform samples
    
    # Context
    activity_type = Column(String(50))  # skiing, shooting, rest, transition
    ski_technique = Column(String(50))  # V1, V2, V2-alternate, etc.
    terrain = Column(String(50))  # uphill, downhill, flat
    
    # Environmental conditions
    altitude = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    
    # Relationships
    athlete = relationship("Athlete", back_populates="sensor_data")
    
    # Indexes for time-series queries
    __table_args__ = (
        Index("idx_sensor_timestamp", "timestamp"),
        Index("idx_sensor_athlete_timestamp", "athlete_id", "timestamp"),
        Index("idx_sensor_activity", "activity_type"),
    )
