"""Athletes API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.athlete import Athlete
from app.schemas.athlete import (
    AthleteCreate,
    AthleteUpdate,
    AthleteResponse,
    AthleteList,
    AthleteCalibration
)
from app.services.athlete_service import AthleteService

router = APIRouter()


@router.get("/", response_model=AthleteList)
async def get_athletes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all athletes with pagination"""
    service = AthleteService(db)
    athletes, total = await service.get_all(skip, limit, active_only)
    
    return AthleteList(
        athletes=athletes,
        total=total
    )


@router.get("/{athlete_id}", response_model=AthleteResponse)
async def get_athlete(
    athlete_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get athlete by ID"""
    service = AthleteService(db)
    athlete = await service.get_by_id(athlete_id)
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    return athlete


@router.post("/", response_model=AthleteResponse, status_code=201)
async def create_athlete(
    athlete_data: AthleteCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new athlete"""
    service = AthleteService(db)
    
    # Check if email already exists
    existing = await service.get_by_email(athlete_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    athlete = await service.create(athlete_data)
    return athlete


@router.patch("/{athlete_id}", response_model=AthleteResponse)
async def update_athlete(
    athlete_id: int,
    update_data: AthleteUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update athlete data"""
    service = AthleteService(db)
    athlete = await service.update(athlete_id, update_data)
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    return athlete


@router.post("/{athlete_id}/calibrate", response_model=AthleteResponse)
async def calibrate_athlete(
    athlete_id: int,
    calibration_data: AthleteCalibration,
    db: AsyncSession = Depends(get_db)
):
    """Upload calibration data for athlete"""
    service = AthleteService(db)
    athlete = await service.calibrate(athlete_id, calibration_data)
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    return athlete


@router.delete("/{athlete_id}", status_code=204)
async def delete_athlete(
    athlete_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Soft delete athlete (set inactive)"""
    service = AthleteService(db)
    success = await service.delete(athlete_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    return None
