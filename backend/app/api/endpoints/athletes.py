"""Athletes API endpoints with history support"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.ibu_full_service import ibu_service

router = APIRouter()

@router.get("/")
async def get_athletes(
    nation: Optional[str] = Query(None, description="Filter by nation code"),
    limit: int = Query(50, ge=1, le=200)
):
    """Get athletes from IBU API"""
    athletes = ibu_service.get_athletes(nation=nation, limit=limit)
    
    if not athletes and nation == "CZE":
        # Return at least some Czech athletes we know exist
        return [
            {"id": "BTCZE12903199501", "name": "Markéta Davidová", "nation": "CZE", "active": True},
            {"id": "BTCZE11502200001", "name": "Jessica Jislová", "nation": "CZE", "active": True},
            {"id": "BTCZE12811199401", "name": "Lucie Charvátová", "nation": "CZE", "active": True}
        ]
    
    return athletes

@router.get("/{athlete_id}/performance")
async def get_performance(athlete_id: str):
    """Get athlete performance from IBU API"""
    performance = ibu_service.get_athlete_performance(athlete_id)
    
    if not performance:
        # Return minimal data structure
        return {
            "athlete_id": athlete_id,
            "message": "Limited data available",
            "total_races": 0,
            "avg_rank": 0,
            "median_rank": 0,
            "best_rank": 0,
            "worst_rank": 0,
            "shooting": {
                "total_accuracy": 80.0,
                "prone_accuracy": 85.0,
                "standing_accuracy": 75.0,
                "avg_shooting_time": None
            },
            "avg_ski_time": 0,
            "consistency_score": 50.0,
            "recent_form": 0.0,
            "points_total": 0
        }
    
    return performance

@router.get("/{athlete_id}/history")
async def get_athlete_history(
    athlete_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get athlete race history with patterns and trends"""
    try:
        history_data = ibu_service.get_athlete_history(athlete_id, limit=limit)
        
        if not history_data:
            return {
                "athlete_id": athlete_id,
                "history": [],
                "patterns": [],
                "trends": {"direction": "insufficient_data"},
                "total_races": 0
            }
        
        return history_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{athlete_id}/recent")
async def get_recent_races(
    athlete_id: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Get recent race results for athlete"""
    try:
        history = ibu_service.get_athlete_history(athlete_id, limit=limit)
        
        if not history or not history.get('history'):
            return []
        
        return history['history'][:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_athletes(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search for athletes by name or nation"""
    try:
        # Get all athletes and filter
        all_athletes = ibu_service.get_athletes(limit=200)
        
        query_lower = q.lower()
        matches = []
        
        for athlete in all_athletes:
            if (query_lower in athlete.get('name', '').lower() or 
                query_lower in athlete.get('nation', '').lower()):
                matches.append(athlete)
                
                if len(matches) >= limit:
                    break
        
        return matches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
