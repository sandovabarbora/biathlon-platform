"""Race analysis endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.ibu_full_service import ibu_service

router = APIRouter()

@router.get("/")
async def get_races(
    limit: int = Query(20, ge=1, le=100)
):
    """Get recent races"""
    try:
        races = ibu_service.get_recent_races(limit=limit)
        return races
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming")
async def get_upcoming_races():
    """Get upcoming races with Czech participation prediction"""
    try:
        races = ibu_service.get_upcoming_races()
        return races
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/last")
async def get_last_race():
    """Get the most recent race with Czech athletes"""
    try:
        races = ibu_service.get_recent_races(limit=5)
        
        # Find first race with Czech athletes
        for race in races:
            analysis = ibu_service.get_race_analysis(race['race_id'])
            if analysis and analysis.get('czech_athletes'):
                return analysis
        
        # Return first race if no Czech found
        if races:
            return ibu_service.get_race_analysis(races[0]['race_id'])
        
        return None
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{race_id}/analysis")
async def get_race_analysis(race_id: str):
    """Get detailed race analysis with Czech focus"""
    try:
        analysis = ibu_service.get_race_analysis(race_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Race not found")
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{race_id}/czechs")
async def get_czech_performance(race_id: str):
    """Get Czech athletes performance in specific race"""
    try:
        analysis = ibu_service.get_race_analysis(race_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Race not found")
        
        return {
            "race_id": race_id,
            "competition": analysis.get('competition'),
            "czech_athletes": analysis.get('czech_athletes', []),
            "best_czech": min(
                analysis.get('czech_athletes', []),
                key=lambda x: x.get('rank', 999),
                default=None
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
