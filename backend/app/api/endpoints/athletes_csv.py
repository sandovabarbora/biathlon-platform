"""Athletes API endpoints using CSV data"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.data_service import data_service
from app.api.schemas import PerformanceStats, TrainingRecommendation

router = APIRouter()

@router.get("/")
async def get_athletes(
    nation: Optional[str] = Query(None, description="Filter by nation (e.g., CZE)"),
    limit: int = Query(100, ge=1, le=500)
):
    """Get list of athletes from CSV data"""
    athletes = data_service.get_athletes(nation=nation, limit=limit)
    return athletes

@router.get("/{athlete_id}/performance")
async def get_performance(athlete_id: str):
    """Get athlete performance from CSV data"""
    performance = data_service.get_athlete_performance(athlete_id)
    
    if not performance:
        raise HTTPException(status_code=404, detail=f"Athlete {athlete_id} not found")
    
    # Convert to Pydantic model format
    return {
        "athlete_id": performance['athlete_id'],
        "total_races": performance['total_races'],
        "avg_rank": performance['avg_rank'],
        "median_rank": performance['median_rank'],
        "best_rank": performance['best_rank'],
        "worst_rank": performance['worst_rank'],
        "shooting": {
            "total_accuracy": performance['shooting']['total_accuracy'],
            "prone_accuracy": performance['shooting']['prone_accuracy'],
            "standing_accuracy": performance['shooting']['standing_accuracy'],
            "avg_shooting_time": performance['shooting'].get('avg_shooting_time')
        },
        "avg_ski_time": 0,  # Calculate from data if needed
        "consistency_score": performance['consistency_score'],
        "recent_form": performance['recent_form'],
        "points_total": performance['points_total']
    }

@router.get("/search")
async def search_athletes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20)
):
    """Search athletes by name"""
    all_athletes = data_service.get_athletes(limit=1000)
    
    # Filter by search query
    query_lower = q.lower()
    matches = [
        a for a in all_athletes 
        if query_lower in a['name'].lower() or query_lower in a['nation'].lower()
    ]
    
    return matches[:limit]

@router.get("/top-czech")
async def get_top_czech_athletes():
    """Get top Czech athletes"""
    return data_service.get_athletes(nation="CZE", limit=20)
