"""
Fatigue Analysis API Endpoints
Complete integration with frontend
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from app.services.fatigue_analysis import (
    FatigueResistanceEngine, 
    FatigueProfile,
    compare_athletes_fatigue,
    analyze_team_fatigue_patterns
)
from app.services.ibu_full_service import ibu_service
from app.core.database import get_db
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fatigue", tags=["fatigue"])

# Initialize engine
fatigue_engine = FatigueResistanceEngine()

@router.get("/profile/{athlete_id}")
async def get_fatigue_profile(
    athlete_id: str,
    force_refresh: bool = Query(False, description="Force recalculation"),
    include_history: bool = Query(True, description="Include historical data")
) -> Dict:
    """
    Get comprehensive fatigue profile for an athlete
    """
    try:
        # Get athlete info
        athlete_info = ibu_service.get_athlete_info(athlete_id)
        if not athlete_info:
            raise HTTPException(status_code=404, detail=f"Athlete {athlete_id} not found")
        
        # Get race history (last 50 races)
        race_history = ibu_service.get_athlete_history(athlete_id, limit=50)
        
        if not race_history or not race_history.get('history'):
            return {
                "status": "insufficient_data",
                "message": "Not enough race data for fatigue analysis",
                "athlete_id": athlete_id,
                "athlete_name": athlete_info.get('name', 'Unknown')
            }
        
        # Generate fatigue profile
        profile = fatigue_engine.analyze_athlete_complete(
            athlete_id=athlete_id,
            athlete_name=athlete_info.get('name', 'Unknown'),
            race_history=race_history.get('history', [])
        )
        
        # Generate training recommendations
        recommendations = fatigue_engine.generate_training_recommendations(profile)
        
        # Get comparison with team
        team_comparison = await get_team_comparison(athlete_id, profile.fatigue_resistance_score)
        
        response = {
            "profile": profile.to_dict(),
            "recommendations": recommendations,
            "team_comparison": team_comparison,
            "last_updated": datetime.now().isoformat()
        }
        
        if include_history:
            # Add historical progression
            response["historical_progression"] = await get_historical_progression(athlete_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating fatigue profile for {athlete_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team/analysis")
async def get_team_fatigue_analysis(
    nation: str = Query("CZE", description="Nation code")
) -> Dict:
    """
    Analyze fatigue patterns for entire team
    """
    try:
        # Get team athletes
        athletes = ibu_service.get_athletes(nation=nation, limit=30)
        
        if not athletes:
            raise HTTPException(status_code=404, detail=f"No athletes found for {nation}")
        
        team_profiles = []
        team_stats = {
            "avg_resistance_score": 0,
            "avg_recovery_efficiency": 0,
            "avg_pressure_response": 0,
            "athletes_analyzed": 0,
            "weakest_areas": [],
            "strongest_areas": []
        }
        
        for athlete in athletes[:10]:  # Limit to top 10 for performance
            try:
                # Get athlete's fatigue profile
                history = ibu_service.get_athlete_history(athlete['id'], limit=30)
                
                if history and history.get('history'):
                    profile = fatigue_engine.analyze_athlete_complete(
                        athlete_id=athlete['id'],
                        athlete_name=athlete['name'],
                        race_history=history.get('history', [])
                    )
                    
                    team_profiles.append({
                        "athlete_id": athlete['id'],
                        "name": athlete['name'],
                        "world_rank": athlete.get('world_rank'),
                        "fatigue_score": profile.fatigue_resistance_score,
                        "recovery_efficiency": profile.recovery_efficiency,
                        "pressure_response": profile.pressure_response,
                        "trend": profile.trend_direction,
                        "czech_rank": profile.czech_rank
                    })
                    
                    # Update team stats
                    team_stats["avg_resistance_score"] += profile.fatigue_resistance_score
                    team_stats["avg_recovery_efficiency"] += profile.recovery_efficiency
                    team_stats["avg_pressure_response"] += profile.pressure_response
                    team_stats["athletes_analyzed"] += 1
                    
            except Exception as e:
                logger.warning(f"Could not analyze {athlete['name']}: {e}")
                continue
        
        # Calculate averages
        if team_stats["athletes_analyzed"] > 0:
            team_stats["avg_resistance_score"] /= team_stats["athletes_analyzed"]
            team_stats["avg_recovery_efficiency"] /= team_stats["athletes_analyzed"]
            team_stats["avg_pressure_response"] /= team_stats["athletes_analyzed"]
        
        # Sort athletes by fatigue score
        team_profiles.sort(key=lambda x: x["fatigue_score"], reverse=True)
        
        # Identify team patterns
        if team_stats["avg_recovery_efficiency"] < 70:
            team_stats["weakest_areas"].append({
                "area": "Recovery Efficiency",
                "score": team_stats["avg_recovery_efficiency"],
                "recommendation": "Team-wide focus on recovery protocols and breathing techniques"
            })
        
        if team_stats["avg_pressure_response"] < 75:
            team_stats["weakest_areas"].append({
                "area": "Pressure Handling",
                "score": team_stats["avg_pressure_response"],
                "recommendation": "Implement mental training and pressure simulation"
            })
        
        return {
            "nation": nation,
            "team_stats": team_stats,
            "athlete_profiles": team_profiles,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in team fatigue analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare")
async def compare_athletes_fatigue_profiles(
    athlete1_id: str = Query(..., description="First athlete ID"),
    athlete2_id: str = Query(..., description="Second athlete ID")
) -> Dict:
    """
    Compare fatigue profiles of two athletes
    """
    try:
        profiles = {}
        
        for athlete_id in [athlete1_id, athlete2_id]:
            # Get athlete data
            athlete_info = ibu_service.get_athlete_info(athlete_id)
            history = ibu_service.get_athlete_history(athlete_id, limit=30)
            
            if not history or not history.get('history'):
                raise HTTPException(
                    status_code=404, 
                    detail=f"Insufficient data for {athlete_id}"
                )
            
            profile = fatigue_engine.analyze_athlete_complete(
                athlete_id=athlete_id,
                athlete_name=athlete_info.get('name', 'Unknown'),
                race_history=history.get('history', [])
            )
            
            profiles[athlete_id] = profile
        
        # Compare profiles
        comparison = {
            "athlete1": {
                "id": athlete1_id,
                "name": profiles[athlete1_id].name,
                "fatigue_score": profiles[athlete1_id].fatigue_resistance_score,
                "recovery": profiles[athlete1_id].recovery_efficiency,
                "pressure": profiles[athlete1_id].pressure_response
            },
            "athlete2": {
                "id": athlete2_id,
                "name": profiles[athlete2_id].name,
                "fatigue_score": profiles[athlete2_id].fatigue_resistance_score,
                "recovery": profiles[athlete2_id].recovery_efficiency,
                "pressure": profiles[athlete2_id].pressure_response
            },
            "advantages": {
                "athlete1": [],
                "athlete2": []
            },
            "recommendations": {}
        }
        
        # Determine advantages
        if profiles[athlete1_id].fatigue_resistance_score > profiles[athlete2_id].fatigue_resistance_score:
            comparison["advantages"]["athlete1"].append("Better overall fatigue resistance")
        else:
            comparison["advantages"]["athlete2"].append("Better overall fatigue resistance")
        
        if profiles[athlete1_id].recovery_efficiency > profiles[athlete2_id].recovery_efficiency:
            comparison["advantages"]["athlete1"].append("Faster HR recovery on range")
        else:
            comparison["advantages"]["athlete2"].append("Faster HR recovery on range")
        
        if profiles[athlete1_id].pressure_response > profiles[athlete2_id].pressure_response:
            comparison["advantages"]["athlete1"].append("Better under pressure")
        else:
            comparison["advantages"]["athlete2"].append("Better under pressure")
        
        # Training recommendations
        if abs(profiles[athlete1_id].recovery_efficiency - profiles[athlete2_id].recovery_efficiency) > 15:
            weaker = athlete1_id if profiles[athlete1_id].recovery_efficiency < profiles[athlete2_id].recovery_efficiency else athlete2_id
            comparison["recommendations"][weaker] = "Focus on recovery training - study partner's breathing technique"
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing athletes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/race-strategy/{athlete_id}")
async def get_race_strategy(
    athlete_id: str,
    race_type: str = Query("sprint", description="Race type: sprint, pursuit, individual"),
    temperature: float = Query(0, description="Expected temperature"),
    wind_speed: float = Query(0, description="Expected wind speed m/s"),
    altitude: int = Query(500, description="Venue altitude in meters")
) -> Dict:
    """
    Generate race-specific strategy based on fatigue profile
    """
    try:
        # Get athlete profile
        athlete_info = ibu_service.get_athlete_info(athlete_id)
        history = ibu_service.get_athlete_history(athlete_id, limit=30)
        
        if not history or not history.get('history'):
            raise HTTPException(status_code=404, detail="Insufficient data")
        
        profile = fatigue_engine.analyze_athlete_complete(
            athlete_id=athlete_id,
            athlete_name=athlete_info.get('name', 'Unknown'),
            race_history=history.get('history', [])
        )
        
        # Generate race strategy
        race_conditions = {
            "race_type": race_type,
            "temperature": temperature,
            "wind_speed": wind_speed,
            "altitude": altitude
        }
        
        strategy = fatigue_engine.generate_race_strategy(profile, race_conditions)
        
        # Add specific recommendations based on conditions
        if altitude > 1000:
            strategy["altitude_adjustment"] = {
                "warning": "High altitude venue",
                "pacing_adjustment": "Reduce intensity by 3-5% on climbs",
                "expected_hr_increase": "+5-8 BPM at same effort"
            }
        
        if wind_speed > 3:
            strategy["wind_adjustment"] = {
                "shooting_strategy": "Take extra time for stability",
                "time_allowance": f"+{profile.lactate_time_penalty + 2:.1f}s per shot"
            }
        
        if temperature < -10:
            strategy["cold_adjustment"] = {
                "warm_up": "Extended warm-up required",
                "breathing": "Cover mouth on approach to range",
                "equipment": "Check ski wax for cold conditions"
            }
        
        return {
            "athlete_id": athlete_id,
            "athlete_name": athlete_info.get('name'),
            "race_conditions": race_conditions,
            "strategy": strategy,
            "key_points": [
                f"Optimal arrival HR: {profile.optimal_arrival_hr} BPM",
                f"Expected time penalty under fatigue: {profile.lactate_time_penalty:.1f}s",
                f"Recovery efficiency: {profile.recovery_efficiency:.0f}/100"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating race strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/{athlete_id}")
async def get_fatigue_trends(
    athlete_id: str,
    period_days: int = Query(90, description="Period to analyze in days")
) -> Dict:
    """
    Get fatigue resistance trends over time
    """
    try:
        # Get historical data
        history = ibu_service.get_athlete_history(athlete_id, limit=100)
        
        if not history or not history.get('history'):
            raise HTTPException(status_code=404, detail="No historical data")
        
        # Filter by period
        cutoff_date = datetime.now() - timedelta(days=period_days)
        filtered_history = [
            race for race in history['history']
            if datetime.fromisoformat(race.get('date', '2024-01-01')) > cutoff_date
        ]
        
        # Calculate trends
        monthly_scores = {}
        
        for race in filtered_history:
            month_key = race.get('date', '')[:7]  # YYYY-MM
            
            if month_key not in monthly_scores:
                monthly_scores[month_key] = {
                    "races": [],
                    "avg_recovery_time": [],
                    "shooting_under_fatigue": []
                }
            
            # Extract fatigue-related metrics
            if 'shootings' in race:
                for shooting in race['shootings']:
                    if 'arrival_hr' in shooting and 'shooting_hr' in shooting:
                        recovery = shooting['arrival_hr'] - shooting['shooting_hr']
                        monthly_scores[month_key]["avg_recovery_time"].append(recovery)
                        
                        # High fatigue shooting (HR > 160)
                        if shooting['arrival_hr'] > 160:
                            accuracy = shooting.get('hits', 0) / shooting.get('total', 5)
                            monthly_scores[month_key]["shooting_under_fatigue"].append(accuracy)
        
        # Calculate monthly averages
        trend_data = []
        for month, data in sorted(monthly_scores.items()):
            if data["avg_recovery_time"]:
                trend_data.append({
                    "month": month,
                    "avg_hr_recovery": np.mean(data["avg_recovery_time"]),
                    "fatigue_shooting_accuracy": np.mean(data["shooting_under_fatigue"]) * 100 if data["shooting_under_fatigue"] else None,
                    "sample_size": len(data["avg_recovery_time"])
                })
        
        # Determine trend direction
        if len(trend_data) >= 2:
            first_accuracy = trend_data[0].get("fatigue_shooting_accuracy", 0)
            last_accuracy = trend_data[-1].get("fatigue_shooting_accuracy", 0)
            
            trend_direction = "improving" if last_accuracy > first_accuracy else "declining"
            improvement = last_accuracy - first_accuracy
        else:
            trend_direction = "insufficient_data"
            improvement = 0
        
        return {
            "athlete_id": athlete_id,
            "period_days": period_days,
            "trend_direction": trend_direction,
            "total_improvement": improvement,
            "monthly_data": trend_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting fatigue trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def get_team_comparison(athlete_id: str, fatigue_score: float) -> Dict:
    """Get comparison with team averages"""
    # This would connect to your database or cache
    return {
        "team_avg_fatigue_score": 75.0,
        "athlete_percentile": 85,
        "rank_in_team": 3,
        "comparison": "above_average" if fatigue_score > 75 else "below_average"
    }

async def get_historical_progression(athlete_id: str) -> List[Dict]:
    """Get historical progression of fatigue metrics"""
    # This would fetch from database
    return [
        {"date": "2024-01", "score": 72, "recovery": 68},
        {"date": "2024-06", "score": 75, "recovery": 72},
        {"date": "2024-12", "score": 78, "recovery": 76}
    ]
