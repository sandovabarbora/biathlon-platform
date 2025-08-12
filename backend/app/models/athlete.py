"""SQLAlchemy models"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Athlete(Base):
    __tablename__ = "athletes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    nation = Column(String(3), nullable=False, index=True)
    birth_date = Column(DateTime, nullable=True)
    ibu_id = Column(String, unique=True, nullable=True)
    active = Column(Boolean, default=True)
    
    # Relationships
    results = relationship("RaceResult", back_populates="athlete")

class Race(Base):
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    event_type = Column(String, nullable=False)  # Sprint, Pursuit, Individual, Mass Start
    gender = Column(String(1), nullable=False)  # M, W
    distance = Column(Float)  # km
    
    # Relationships
    results = relationship("RaceResult", back_populates="race")

class RaceResult(Base):
    __tablename__ = "race_results"
    
    id = Column(Integer, primary_key=True, index=True)
    athlete_id = Column(Integer, ForeignKey("athletes.id"))
    race_id = Column(Integer, ForeignKey("races.id"))
    
    rank = Column(Integer)
    bib = Column(Integer)
    shooting_total = Column(Integer)  # Total misses
    shooting_prone = Column(String)    # "0+1" format
    shooting_standing = Column(String) # "1+2" format
    ski_time = Column(Float)          # seconds
    total_time = Column(Float)        # seconds
    time_behind = Column(Float)       # seconds
    
    # Relationships
    athlete = relationship("Athlete", back_populates="results")
    race = relationship("Race", back_populates="results")
