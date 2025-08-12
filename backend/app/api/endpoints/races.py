"""Race endpoints with real data"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from app.services.ibu_full_service import ibu_service

router = APIRouter()

@router.get("/recent", response_model=List[Dict])
async def get_recent_races(limit: int = Query(10, ge=1, le=50)):
    """Get recent races"""
    races = ibu_service.get_recent_races(limit)
    return races

@router.get("/upcoming", response_model=List[Dict])
async def get_upcoming_races():
    """Get upcoming races"""
    races = ibu_service.get_upcoming_races()
    return races

@router.get("/{race_id}/analysis")
async def get_race_analysis(race_id: str):
    """Get detailed race analysis"""
    analysis = ibu_service.get_race_analysis(race_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Race not found")
    return analysis

@router.get("/{race_id}/live")
async def get_live_data(race_id: str):
    """Get live race data (simulated)"""
    # V reálné aplikaci by to bylo napojené na WebSocket
    return {
        "race_id": race_id,
        "status": "in_progress",
        "current_loop": 2,
        "leaders": [
            {"position": 1, "name": "OEBERG E.", "nation": "SWE", "time": "12:34.5"},
            {"position": 2, "name": "DAVIDOVA M.", "nation": "CZE", "time": "+8.3"}
        ],
        "weather": {
            "temperature": -5,
            "wind_speed": 2.3,
            "conditions": "Light snow"
        }
    }
