"""Digital Twin API endpoints"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, List, Optional
from app.services.digital_twin import (
    create_athlete_twin,
    simulate_race_scenario,
    analyze_what_if,
    generate_optimal_training,
    digital_twin_engine
)
from app.services.ibu_full_service import ibu_service

router = APIRouter()

@router.post("/{athlete_id}/create")
async def create_twin(athlete_id: str):
    """Create digital twin for athlete"""
    try:
        # Get athlete data
        athlete_data = {
            'id': athlete_id,
            'name': 'Czech Athlete',
            'world_rank': 30,
            'age': 25,
            'weight': 60,
            'height': 170
        }
        
        # Try to get real data from IBU
        try:
            performance = ibu_service.get_athlete_performance(athlete_id)
            if performance:
                athlete_data['world_rank'] = performance.get('avg_rank', 30)
        except:
            pass
        
        result = create_athlete_twin(athlete_id, athlete_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{athlete_id}/simulate")
async def simulate_race(
    athlete_id: str,
    race_params: Dict = Body(...)
):
    """Simulate race for athlete's digital twin"""
    try:
        result = simulate_race_scenario(athlete_id, race_params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{athlete_id}/what-if")
async def what_if_analysis(
    athlete_id: str,
    scenario: Dict = Body(...)
):
    """Run what-if scenario analysis"""
    try:
        result = analyze_what_if(athlete_id, scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{athlete_id}/optimize-training")
async def optimize_training(
    athlete_id: str,
    goals: Dict = Body(...)
):
    """Generate optimal training plan"""
    try:
        result = generate_optimal_training(athlete_id, goals)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{athlete_id}/status")
async def get_twin_status(athlete_id: str):
    """Get digital twin status"""
    
    if athlete_id not in digital_twin_engine.twins:
        return {
            'exists': False,
            'athlete_id': athlete_id
        }
    
    twin = digital_twin_engine.twins[athlete_id]
    
    return {
        'exists': True,
        'athlete_id': athlete_id,
        'name': twin.name,
        'parameters': {
            'vo2_max': twin.vo2_max,
            'hr_max': twin.hr_max,
            'lactate_threshold': twin.lactate_threshold,
            'ski_efficiency': twin.ski_efficiency,
            'shooting_technique': twin.shooting_technique
        },
        'simulations_run': len([s for s in digital_twin_engine.simulations if s.get('athlete_id') == athlete_id])
    }

@router.post("/{athlete_id}/batch-scenarios")
async def batch_scenarios(
    athlete_id: str,
    scenarios: List[Dict] = Body(...)
):
    """Run multiple what-if scenarios"""
    
    results = []
    for scenario in scenarios:
        try:
            result = analyze_what_if(athlete_id, scenario)
            results.append({
                'scenario': scenario.get('name', 'Unnamed'),
                'result': result
            })
        except Exception as e:
            results.append({
                'scenario': scenario.get('name', 'Unnamed'),
                'error': str(e)
            })
    
    return {
        'athlete_id': athlete_id,
        'scenarios_run': len(results),
        'results': results
    }
