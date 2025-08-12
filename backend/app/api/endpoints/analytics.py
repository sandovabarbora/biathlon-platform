"""Analytics API endpoints with head-to-head and history"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.ibu_full_service import ibu_service
from app.services.training_service import training_service
from app.api.schemas import TrainingRecommendation

router = APIRouter()

@router.get("/training/{athlete_id}", response_model=List[TrainingRecommendation])
async def get_training_recommendations(athlete_id: str):
    """Get training recommendations for athlete"""
    recommendations = training_service.generate_recommendations(athlete_id)
    
    if not recommendations:
        return [TrainingRecommendation(
            priority="MEDIUM",
            area="General Training",
            description="Continue balanced training program",
            expected_impact="Maintain current performance level",
            exercises=[
                "Regular shooting practice",
                "Aerobic base training",
                "Strength maintenance",
                "Mental preparation"
            ],
            metrics_to_track=["Training hours", "Shooting accuracy", "Physical tests"]
        )]
    
    return recommendations

@router.get("/head-to-head")
async def get_head_to_head(
    athlete1: str = Query(..., description="First athlete IBU ID"),
    athlete2: str = Query(..., description="Second athlete IBU ID")
):
    """Get head-to-head comparison between two athletes"""
    try:
        h2h_data = ibu_service.get_head_to_head(athlete1, athlete2)
        
        if not h2h_data:
            return {
                "total_races": 0,
                "athlete1_wins": 0,
                "athlete2_wins": 0,
                "message": "No common races found"
            }
        
        return h2h_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comparison")
async def compare_athletes(
    athlete1: str = Query(..., description="First athlete IBU ID"),
    athlete2: str = Query(..., description="Second athlete IBU ID")
):
    """Get detailed performance comparison"""
    try:
        # Get both performances
        perf1 = ibu_service.get_athlete_performance(athlete1)
        perf2 = ibu_service.get_athlete_performance(athlete2)
        
        if not perf1 or not perf2:
            raise HTTPException(status_code=404, detail="One or both athletes not found")
        
        # Calculate differences
        comparison = {
            "athlete1": perf1,
            "athlete2": perf2,
            "advantages": {
                "athlete1": [],
                "athlete2": []
            }
        }
        
        # Determine advantages
        if perf1['avg_rank'] < perf2['avg_rank']:
            comparison['advantages']['athlete1'].append("Better average ranking")
        else:
            comparison['advantages']['athlete2'].append("Better average ranking")
        
        if perf1['shooting']['total_accuracy'] > perf2['shooting']['total_accuracy']:
            comparison['advantages']['athlete1'].append("Superior shooting accuracy")
        else:
            comparison['advantages']['athlete2'].append("Superior shooting accuracy")
        
        if perf1.get('ski_stats', {}).get('ski_speed_percentile', 0) > perf2.get('ski_stats', {}).get('ski_speed_percentile', 0):
            comparison['advantages']['athlete1'].append("Faster skiing")
        else:
            comparison['advantages']['athlete2'].append("Faster skiing")
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/{athlete_id}")
async def get_athlete_trends(
    athlete_id: str,
    period: str = Query("season", pattern="^(month|season|year)$")
):
    """Get performance trends for athlete"""
    try:
        history = ibu_service.get_athlete_history(athlete_id, limit=50)
        
        if not history or not history.get('history'):
            raise HTTPException(status_code=404, detail="No history found")
        
        # Calculate trends based on period
        trends = history.get('trends', {})
        patterns = history.get('patterns', [])
        
        return {
            "athlete_id": athlete_id,
            "period": period,
            "trends": trends,
            "patterns": patterns,
            "races_analyzed": len(history.get('history', []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
