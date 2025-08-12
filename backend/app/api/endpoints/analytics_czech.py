"""Czech-focused analytics endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.ibu_service import ibu_service

router = APIRouter()

@router.get("/czech-dashboard")
async def get_czech_dashboard():
    """Main dashboard - Czech athletes with comparison to world"""
    dashboard = ibu_service.get_czech_dashboard()
    
    if not dashboard:
        raise HTTPException(status_code=503, detail="Unable to load data")
    
    return dashboard

@router.get("/athlete/{ibu_id}/vs-world")
async def athlete_vs_world(
    ibu_id: str,
    compare_with: Optional[str] = Query(None, description="IBU ID to compare with")
):
    """Get athlete performance with world comparison"""
    
    performance = ibu_service.get_athlete_performance(ibu_id)
    
    if not performance:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # Add comparison if requested
    if compare_with:
        comparison = ibu_service.get_athlete_performance(compare_with)
        if comparison:
            performance['direct_comparison'] = {
                'athlete': comparison['name'],
                'rank_diff': performance['season_stats']['avg_rank'] - comparison['season_stats']['avg_rank'],
                'shooting_diff': performance['shooting']['avg_misses'] - comparison['shooting']['avg_misses'],
                'ski_diff': performance['skiing']['avg_rank'] - comparison['skiing']['avg_rank']
            }
    
    return performance

@router.get("/race/{race_id}/czech-analysis")
async def analyze_race_czech(race_id: str):
    """Analyze race with focus on Czech performance"""
    
    analysis = ibu_service.get_race_analysis(race_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Race not found")
    
    return analysis

@router.get("/training-priorities")
async def get_training_priorities():
    """Get training priorities for Czech team"""
    
    dashboard = ibu_service.get_czech_dashboard()
    
    priorities = []
    
    # Analyze each athlete
    for athlete in dashboard['athletes']:
        perf = athlete['performance']
        
        # Individual priorities
        athlete_priorities = []
        
        if perf['shooting']['percentile'] < 50:
            athlete_priorities.append({
                'area': 'Shooting',
                'urgency': 'HIGH' if perf['shooting']['percentile'] < 30 else 'MEDIUM',
                'specific': f"Currently {perf['shooting']['avg_misses']:.1f} misses per race"
            })
        
        if perf['skiing']['percentile'] < 50:
            athlete_priorities.append({
                'area': 'Skiing',
                'urgency': 'HIGH' if perf['skiing']['percentile'] < 30 else 'MEDIUM',
                'specific': f"Ski rank {perf['skiing']['avg_rank']:.0f} vs overall rank"
            })
        
        priorities.append({
            'athlete': athlete['name'],
            'world_rank': athlete.get('world_rank'),
            'status': athlete['status'],
            'priorities': athlete_priorities
        })
    
    # Sort by world rank (best athletes first)
    priorities.sort(key=lambda x: x.get('world_rank', 999))
    
    return {
        'individual_priorities': priorities,
        'team_priorities': dashboard['team_stats']['priorities'],
        'recommendation': _generate_team_recommendation(priorities)
    }

def _generate_team_recommendation(priorities: list) -> dict:
    """Generate overall team training recommendation"""
    
    shooting_issues = sum(1 for p in priorities 
                         for pr in p['priorities'] 
                         if pr['area'] == 'Shooting')
    
    skiing_issues = sum(1 for p in priorities 
                       for pr in p['priorities'] 
                       if pr['area'] == 'Skiing')
    
    if shooting_issues > skiing_issues:
        return {
            'focus': 'SHOOTING CAMP',
            'duration': '1 week intensive',
            'details': 'Focus on standing shooting and pressure situations'
        }
    else:
        return {
            'focus': 'ALTITUDE TRAINING',
            'duration': '2 weeks',
            'details': 'Build aerobic base and improve ski speed'
        }

@router.get("/medal-chances")
async def get_medal_chances():
    """Calculate medal chances for Czech athletes"""
    
    dashboard = ibu_service.get_czech_dashboard()
    
    chances = []
    
    for athlete in dashboard['athletes']:
        if athlete.get('world_rank', 999) < 40:
            perf = athlete['performance']
            
            # Simple medal chance calculation
            medal_chance = 0
            
            if perf['season_stats']['best_rank'] <= 3:
                medal_chance = 30  # Has been on podium
            elif perf['season_stats']['best_rank'] <= 6:
                medal_chance = 15  # Close to podium
            elif perf['season_stats']['best_rank'] <= 10:
                medal_chance = 5   # Outside chance
            
            # Adjust for trend
            if perf['trend']['direction'] == 'improving_fast':
                medal_chance *= 1.5
            elif perf['trend']['direction'] == 'declining_fast':
                medal_chance *= 0.5
            
            chances.append({
                'athlete': athlete['name'],
                'world_rank': athlete.get('world_rank'),
                'medal_chance': min(medal_chance, 50),  # Cap at 50%
                'best_discipline': _identify_best_discipline(perf),
                'key_factor': _identify_key_success_factor(perf)
            })
    
    # Sort by medal chance
    chances.sort(key=lambda x: x['medal_chance'], reverse=True)
    
    return chances

def _identify_best_discipline(performance: dict) -> str:
    """Identify athlete's best discipline"""
    
    # Based on shooting/skiing balance
    if performance['shooting']['percentile'] > performance['skiing']['percentile'] + 20:
        return "Individual (shooting advantage)"
    elif performance['skiing']['percentile'] > performance['shooting']['percentile'] + 20:
        return "Sprint (skiing strength)"
    else:
        return "Pursuit (balanced skills)"

def _identify_key_success_factor(performance: dict) -> str:
    """Identify what athlete needs for success"""
    
    if performance['shooting']['avg_misses'] > 3:
        return "Must improve shooting to compete"
    elif performance['skiing']['percentile'] < 40:
        return "Needs better ski speed"
    elif performance['trend']['direction'] == 'improving_fast':
        return "Momentum is key - maintain form"
    else:
        return "Consistency in execution"
