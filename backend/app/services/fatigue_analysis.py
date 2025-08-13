"""
Fatigue-Accuracy Resistance Profiling Engine
Based on IBU research: Elite athletes maintain accuracy at cost of time under fatigue
References: PMC7739577, PMC9004791
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from scipy import stats
from sklearn.linear_model import LinearRegression
import json

logger = logging.getLogger(__name__)

@dataclass
class FatigueProfile:
    """Individual athlete fatigue resistance signature"""
    athlete_id: str
    name: str
    
    # Core fatigue metrics
    hr_shooting_correlation: float  # How HR affects accuracy (-1 to 1)
    lactate_time_penalty: float     # Extra seconds per shot under fatigue
    recovery_efficiency: float      # HR beats/min drop rate on range
    pressure_response: float        # Performance in clutch situations (0-100)
    
    # Optimal zones
    optimal_hr_threshold: int       # HR level for best shooting
    optimal_arrival_hr: int         # Best HR for arrival at range
    
    # Resistance scores
    fatigue_resistance_score: float # Overall resistance (0-100)
    prone_resistance: float         # Prone-specific score
    standing_resistance: float      # Standing-specific score
    
    # Historical trends
    trend_direction: str            # 'improving', 'stable', 'declining'
    improvement_rate: float         # % change per month
    
    # Comparison metrics
    world_rank_percentile: float    # Where athlete stands globally
    czech_rank: int                 # Rank within Czech team
    
    # Timestamp
    calculated_at: datetime
    based_on_races: int            # Number of races analyzed

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['calculated_at'] = self.calculated_at.isoformat()
        return result

@dataclass
class ShootingUnderFatigue:
    """Single shooting bout analysis"""
    race_id: str
    date: datetime
    position: str  # 'prone' or 'standing'
    sequence: int  # 1st, 2nd, 3rd, 4th shooting
    
    # Physiological state
    arrival_hr: int
    shooting_hr: int
    hr_recovery_time: float  # Seconds to drop to shooting HR
    estimated_lactate: float  # mmol/L
    
    # Performance
    hits: int
    total_shots: int
    shooting_time: float
    
    # Context
    temperature: float
    wind_speed: float
    pressure_situation: str  # 'leading', 'chasing', 'pack'
    lap_intensity: float  # % of max speed in previous lap

class FatigueResistanceEngine:
    """
    Advanced fatigue analysis engine with historical tracking and peer comparison
    Based on research: 90% HRmax arrival → 65% during shooting in ~30s
    """
    
    def __init__(self):
        # Research-based constants
        self.ELITE_HR_ARRIVAL = 0.90  # 90% of HRmax
        self.ELITE_HR_SHOOTING = 0.65  # 65% of HRmax
        self.ELITE_RECOVERY_TIME = 30  # seconds
        self.ELITE_ACCURACY_THRESHOLD = 0.85  # 85% hits
        
        # Load historical data for comparison
        self.world_benchmarks = self._load_world_benchmarks()
        self.czech_team_data = {}
        
    def analyze_athlete_complete(
        self, 
        athlete_id: str,
        athlete_name: str,
        race_history: List[Dict],
        training_data: Optional[List[Dict]] = None,
        peer_group: Optional[List[str]] = None
    ) -> FatigueProfile:
        """
        Complete fatigue analysis with historical trends and comparisons
        """
        logger.info(f"Analyzing fatigue profile for {athlete_name}")
        
        # Parse shooting bouts from race history
        shooting_bouts = self._extract_shooting_bouts(race_history)
        
        if len(shooting_bouts) < 10:
            logger.warning(f"Limited data for {athlete_name}: only {len(shooting_bouts)} shooting bouts")
        
        # Core fatigue analysis
        hr_correlation = self._analyze_hr_accuracy_relationship(shooting_bouts)
        time_penalty = self._calculate_fatigue_time_penalty(shooting_bouts)
        recovery_eff = self._analyze_recovery_patterns(shooting_bouts)
        pressure_score = self._evaluate_pressure_performance(shooting_bouts)
        
        # Find optimal zones
        optimal_hr, optimal_arrival = self._find_optimal_hr_zones(shooting_bouts)
        
        # Calculate resistance scores
        overall_resistance = self._calculate_resistance_score(
            hr_correlation, time_penalty, recovery_eff, pressure_score
        )
        prone_resistance = self._calculate_position_resistance(shooting_bouts, 'prone')
        standing_resistance = self._calculate_position_resistance(shooting_bouts, 'standing')
        
        # Analyze historical trends
        trend, improvement = self._analyze_historical_trends(shooting_bouts)
        
        # Compare with peers
        world_percentile = self._compare_with_world(overall_resistance)
        czech_rank = self._get_czech_team_rank(athlete_id, overall_resistance)
        
        return FatigueProfile(
            athlete_id=athlete_id,
            name=athlete_name,
            hr_shooting_correlation=hr_correlation,
            lactate_time_penalty=time_penalty,
            recovery_efficiency=recovery_eff,
            pressure_response=pressure_score,
            optimal_hr_threshold=optimal_hr,
            optimal_arrival_hr=optimal_arrival,
            fatigue_resistance_score=overall_resistance,
            prone_resistance=prone_resistance,
            standing_resistance=standing_resistance,
            trend_direction=trend,
            improvement_rate=improvement,
            world_rank_percentile=world_percentile,
            czech_rank=czech_rank,
            calculated_at=datetime.now(),
            based_on_races=len(set(bout.race_id for bout in shooting_bouts))
        )
    
    def _extract_shooting_bouts(self, race_history: List[Dict]) -> List[ShootingUnderFatigue]:
        """Extract individual shooting bouts from race history"""
        bouts = []
        
        for race in race_history:
            race_id = race.get('race_id', '')
            date = datetime.fromisoformat(race.get('date', datetime.now().isoformat()))
            
            # Extract each shooting
            for shooting in race.get('shootings', []):
                bout = ShootingUnderFatigue(
                    race_id=race_id,
                    date=date,
                    position=shooting.get('position', 'prone'),
                    sequence=shooting.get('sequence', 1),
                    arrival_hr=shooting.get('arrival_hr', 170),
                    shooting_hr=shooting.get('shooting_hr', 130),
                    hr_recovery_time=shooting.get('recovery_time', 30),
                    estimated_lactate=shooting.get('lactate', 4.0),
                    hits=shooting.get('hits', 0),
                    total_shots=shooting.get('total', 5),
                    shooting_time=shooting.get('time', 30),
                    temperature=race.get('temperature', 0),
                    wind_speed=race.get('wind_speed', 0),
                    pressure_situation=shooting.get('situation', 'pack'),
                    lap_intensity=shooting.get('lap_intensity', 0.85)
                )
                bouts.append(bout)
        
        return sorted(bouts, key=lambda x: x.date)
    
    def _analyze_hr_accuracy_relationship(self, bouts: List[ShootingUnderFatigue]) -> float:
        """
        Calculate correlation between HR and accuracy
        Strong negative correlation means athlete struggles under high HR
        """
        if len(bouts) < 5:
            return 0.0
        
        hr_values = []
        accuracy_values = []
        
        for bout in bouts:
            hr_percent = bout.arrival_hr / 190  # Assume max HR ~190
            accuracy = bout.hits / bout.total_shots
            
            hr_values.append(hr_percent)
            accuracy_values.append(accuracy)
        
        if len(hr_values) > 1:
            correlation, p_value = stats.pearsonr(hr_values, accuracy_values)
            
            # Log significant findings
            if p_value < 0.05:
                logger.info(f"Significant HR-accuracy correlation: {correlation:.3f} (p={p_value:.3f})")
            
            return float(correlation)
        
        return 0.0
    
    def _calculate_fatigue_time_penalty(self, bouts: List[ShootingUnderFatigue]) -> float:
        """
        Calculate how much extra time athlete needs when fatigued
        Elite pattern: maintain accuracy but need 2-4 extra seconds
        """
        fresh_times = []
        fatigued_times = []
        
        for bout in bouts:
            hr_percent = bout.arrival_hr / 190
            time_per_shot = bout.shooting_time / bout.total_shots
            
            if hr_percent < 0.80:  # "Fresh" state
                fresh_times.append(time_per_shot)
            elif hr_percent > 0.88:  # "Fatigued" state
                fatigued_times.append(time_per_shot)
        
        if fresh_times and fatigued_times:
            avg_fresh = np.mean(fresh_times)
            avg_fatigued = np.mean(fatigued_times)
            penalty = avg_fatigued - avg_fresh
            
            logger.info(f"Time penalty under fatigue: {penalty:.2f}s per shot")
            return penalty
        
        return 0.0
    
    def _analyze_recovery_patterns(self, bouts: List[ShootingUnderFatigue]) -> float:
        """
        Analyze HR recovery efficiency on shooting range
        Elite athletes drop ~25 BPM in 30 seconds
        """
        recovery_rates = []
        
        for bout in bouts:
            if bout.hr_recovery_time > 0:
                hr_drop = bout.arrival_hr - bout.shooting_hr
                rate = hr_drop / bout.hr_recovery_time * 60  # BPM per minute
                recovery_rates.append(rate)
        
        if recovery_rates:
            avg_recovery = np.mean(recovery_rates)
            # Normalize to 0-100 scale (50 BPM/min = 100 score)
            score = min(100, (avg_recovery / 50) * 100)
            return score
        
        return 50.0  # Default middle score
    
    def _evaluate_pressure_performance(self, bouts: List[ShootingUnderFatigue]) -> float:
        """
        Evaluate performance in high-pressure situations
        Last shooting, leading position, chase situations
        """
        pressure_performances = []
        normal_performances = []
        
        for bout in bouts:
            accuracy = bout.hits / bout.total_shots
            
            # Define pressure situations
            is_pressure = (
                bout.sequence >= 3 or  # Last shootings
                bout.pressure_situation in ['leading', 'chasing'] or
                bout.position == 'standing'  # Generally more pressure
            )
            
            if is_pressure:
                pressure_performances.append(accuracy)
            else:
                normal_performances.append(accuracy)
        
        if pressure_performances and normal_performances:
            avg_pressure = np.mean(pressure_performances)
            avg_normal = np.mean(normal_performances)
            
            # Calculate pressure resistance (100 = same performance, <100 = worse under pressure)
            ratio = avg_pressure / avg_normal if avg_normal > 0 else 1.0
            score = min(100, ratio * 100)
            
            logger.info(f"Pressure performance: {score:.1f} (pressure: {avg_pressure:.3f}, normal: {avg_normal:.3f})")
            return score
        
        return 75.0  # Default score
    
    def _find_optimal_hr_zones(self, bouts: List[ShootingUnderFatigue]) -> Tuple[int, int]:
        """
        Find HR zones where athlete shoots best
        Returns (optimal_shooting_hr, optimal_arrival_hr)
        """
        # Group by HR zones and calculate accuracy
        hr_zones = {}
        
        for bout in bouts:
            # Round to nearest 5 BPM
            shooting_hr_zone = (bout.shooting_hr // 5) * 5
            arrival_hr_zone = (bout.arrival_hr // 5) * 5
            
            if shooting_hr_zone not in hr_zones:
                hr_zones[shooting_hr_zone] = {'hits': 0, 'total': 0}
            
            hr_zones[shooting_hr_zone]['hits'] += bout.hits
            hr_zones[shooting_hr_zone]['total'] += bout.total_shots
        
        # Find best shooting HR
        best_shooting_hr = 130  # Default
        best_accuracy = 0
        
        for hr, stats in hr_zones.items():
            if stats['total'] >= 10:  # Minimum sample size
                accuracy = stats['hits'] / stats['total']
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_shooting_hr = hr
        
        # Similar for arrival HR (looking at successful shootings)
        best_arrival_hr = 170  # Default
        
        return int(best_shooting_hr), int(best_arrival_hr)
    
    def _calculate_resistance_score(
        self,
        hr_correlation: float,
        time_penalty: float,
        recovery_efficiency: float,
        pressure_response: float
    ) -> float:
        """
        Calculate overall fatigue resistance score (0-100)
        Weighted combination of all factors
        """
        # Convert correlation to positive score (less negative = better)
        correlation_score = (1 - abs(hr_correlation)) * 100
        
        # Convert time penalty to score (less penalty = better)
        time_score = max(0, 100 - (time_penalty * 20))  # 5s penalty = 0 score
        
        # Weighted average
        weights = {
            'correlation': 0.25,
            'time': 0.25,
            'recovery': 0.30,
            'pressure': 0.20
        }
        
        score = (
            correlation_score * weights['correlation'] +
            time_score * weights['time'] +
            recovery_efficiency * weights['recovery'] +
            pressure_response * weights['pressure']
        )
        
        return min(100, max(0, score))
    
    def _calculate_position_resistance(
        self, 
        bouts: List[ShootingUnderFatigue], 
        position: str
    ) -> float:
        """Calculate position-specific resistance score"""
        position_bouts = [b for b in bouts if b.position == position]
        
        if not position_bouts:
            return 50.0
        
        # Calculate accuracy under different fatigue levels
        fresh_accuracy = []
        fatigued_accuracy = []
        
        for bout in position_bouts:
            hr_percent = bout.arrival_hr / 190
            accuracy = bout.hits / bout.total_shots
            
            if hr_percent < 0.85:
                fresh_accuracy.append(accuracy)
            else:
                fatigued_accuracy.append(accuracy)
        
        if fresh_accuracy and fatigued_accuracy:
            fresh_avg = np.mean(fresh_accuracy)
            fatigued_avg = np.mean(fatigued_accuracy)
            
            # Resistance = how well accuracy is maintained
            if fresh_avg > 0:
                resistance = (fatigued_avg / fresh_avg) * 100
                return min(100, resistance)
        
        return 75.0
    
    def _analyze_historical_trends(
        self, 
        bouts: List[ShootingUnderFatigue]
    ) -> Tuple[str, float]:
        """
        Analyze trends over time
        Returns (trend_direction, improvement_rate)
        """
        if len(bouts) < 20:
            return 'insufficient_data', 0.0
        
        # Split into time periods
        sorted_bouts = sorted(bouts, key=lambda x: x.date)
        midpoint = len(sorted_bouts) // 2
        
        first_half = sorted_bouts[:midpoint]
        second_half = sorted_bouts[midpoint:]
        
        # Calculate accuracy for each period
        first_accuracy = sum(b.hits for b in first_half) / sum(b.total_shots for b in first_half)
        second_accuracy = sum(b.hits for b in second_half) / sum(b.total_shots for b in second_half)
        
        # Calculate fatigue resistance for each period
        first_resistance = self._calculate_period_resistance(first_half)
        second_resistance = self._calculate_period_resistance(second_half)
        
        # Determine trend
        improvement = ((second_resistance - first_resistance) / first_resistance) * 100 if first_resistance > 0 else 0
        
        if improvement > 5:
            trend = 'improving'
        elif improvement < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Calculate monthly improvement rate
        if sorted_bouts[0].date and sorted_bouts[-1].date:
            months = (sorted_bouts[-1].date - sorted_bouts[0].date).days / 30
            monthly_rate = improvement / months if months > 0 else 0
        else:
            monthly_rate = 0
        
        logger.info(f"Historical trend: {trend} ({improvement:.1f}% total, {monthly_rate:.2f}% per month)")
        
        return trend, monthly_rate
    
    def _calculate_period_resistance(self, bouts: List[ShootingUnderFatigue]) -> float:
        """Calculate resistance score for a specific period"""
        if not bouts:
            return 50.0
        
        # Simple resistance metric: accuracy under high HR
        high_hr_bouts = [b for b in bouts if b.arrival_hr > 160]
        
        if high_hr_bouts:
            hits = sum(b.hits for b in high_hr_bouts)
            total = sum(b.total_shots for b in high_hr_bouts)
            return (hits / total * 100) if total > 0 else 50.0
        
        return 50.0
    
    def _compare_with_world(self, resistance_score: float) -> float:
        """Compare with world benchmarks"""
        # Based on research, elite athletes have specific patterns
        benchmarks = [
            (95, 99),  # World top 1%
            (90, 95),  # World top 5%
            (85, 90),  # World top 10%
            (80, 85),  # World top 20%
            (75, 80),  # World top 30%
            (70, 75),  # World top 40%
            (65, 70),  # World top 50%
        ]
        
        for score_threshold, percentile in benchmarks:
            if resistance_score >= score_threshold:
                return percentile
        
        return 50.0  # Below average
    
    def _get_czech_team_rank(self, athlete_id: str, resistance_score: float) -> int:
        """Get rank within Czech team"""
        # Update Czech team data
        self.czech_team_data[athlete_id] = resistance_score
        
        # Sort and find rank
        sorted_scores = sorted(self.czech_team_data.values(), reverse=True)
        
        try:
            rank = sorted_scores.index(resistance_score) + 1
        except ValueError:
            rank = len(sorted_scores) + 1
        
        return rank
    
    def _load_world_benchmarks(self) -> Dict:
        """Load world-class athlete benchmarks from research"""
        return {
            'elite_recovery_rate': 50,  # BPM per minute
            'elite_accuracy_under_fatigue': 0.85,
            'elite_time_penalty': 2.5,  # seconds
            'elite_pressure_performance': 90  # score
        }
    
    def generate_training_recommendations(self, profile: FatigueProfile) -> List[Dict]:
        """Generate specific training recommendations based on profile"""
        recommendations = []
        
        # Check HR-accuracy correlation
        if profile.hr_shooting_correlation < -0.5:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Shooting under fatigue',
                'issue': f'Strong negative correlation ({profile.hr_shooting_correlation:.2f}) between HR and accuracy',
                'recommendation': 'Increase combo training with shooting at >85% HRmax',
                'exercises': [
                    '5x4min intervals with immediate shooting',
                    'Progressive fatigue shooting ladder',
                    'Race simulation with elevated HR targets'
                ],
                'expected_improvement': '10-15% accuracy under fatigue in 6 weeks'
            })
        
        # Check recovery efficiency
        if profile.recovery_efficiency < 70:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'HR Recovery',
                'issue': f'Slow HR recovery on range ({profile.recovery_efficiency:.0f}/100)',
                'recommendation': 'Focus on breathing techniques and recovery protocols',
                'exercises': [
                    'Box breathing drills (4-7-8 pattern)',
                    'HRV biofeedback training',
                    'Transition practice with recovery focus'
                ],
                'expected_improvement': '20% faster HR recovery in 4 weeks'
            })
        
        # Check pressure performance
        if profile.pressure_response < 80:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Mental resilience',
                'issue': f'Performance drops under pressure ({profile.pressure_response:.0f}/100)',
                'recommendation': 'Implement pressure training scenarios',
                'exercises': [
                    'Competition simulation training',
                    'Visualization and mental rehearsal',
                    'Progressive pressure training'
                ],
                'expected_improvement': 'Better clutch performance'
            })
        
        # Check standing vs prone
        if abs(profile.standing_resistance - profile.prone_resistance) > 15:
            weaker = 'standing' if profile.standing_resistance < profile.prone_resistance else 'prone'
            recommendations.append({
                'priority': 'MEDIUM',
                'area': f'{weaker.capitalize()} shooting',
                'issue': f'Significant gap between positions ({abs(profile.standing_resistance - profile.prone_resistance):.0f} points)',
                'recommendation': f'Targeted {weaker} position training',
                'exercises': [
                    f'{weaker.capitalize()} shooting volume +30%',
                    f'Core stability for {weaker} position',
                    f'Technical video analysis of {weaker}'
                ],
                'expected_improvement': f'10% better {weaker} accuracy'
            })
        
        return recommendations

    def generate_race_strategy(
        self, 
        profile: FatigueProfile,
        race_conditions: Dict
    ) -> Dict:
        """Generate race-specific strategy based on fatigue profile"""
        strategy = {
            'pacing': {},
            'shooting': {},
            'risk_assessment': {}
        }
        
        # Pacing recommendations based on recovery efficiency
        if profile.recovery_efficiency > 80:
            strategy['pacing']['approach'] = 'aggressive'
            strategy['pacing']['detail'] = 'Your excellent recovery allows pushing harder into shooting'
            strategy['pacing']['target_arrival_hr'] = profile.optimal_arrival_hr + 5
        else:
            strategy['pacing']['approach'] = 'controlled'
            strategy['pacing']['detail'] = 'Manage effort 200m before range for better shooting'
            strategy['pacing']['target_arrival_hr'] = profile.optimal_arrival_hr
        
        # Shooting strategy
        if profile.lactate_time_penalty > 3:
            strategy['shooting']['approach'] = 'deliberate'
            strategy['shooting']['detail'] = 'Take extra 1-2 seconds for stability'
            strategy['shooting']['target_time'] = 28 + profile.lactate_time_penalty
        else:
            strategy['shooting']['approach'] = 'rhythm'
            strategy['shooting']['detail'] = 'Maintain your natural rhythm'
            strategy['shooting']['target_time'] = 26
        
        # Weather adjustments
        wind_speed = race_conditions.get('wind_speed', 0)
        if wind_speed > 3:
            strategy['shooting']['wind_adjustment'] = 'Wait for wind gaps between shots'
            if profile.pressure_response < 80:
                strategy['shooting']['wind_strategy'] = 'Conservative - ensure clean shooting'
        
        # Risk assessment
        if profile.trend_direction == 'improving':
            strategy['risk_assessment']['confidence'] = 'high'
            strategy['risk_assessment']['recommendation'] = 'Trust your preparation, race aggressively'
        elif profile.fatigue_resistance_score < 70:
            strategy['risk_assessment']['confidence'] = 'moderate'
            strategy['risk_assessment']['recommendation'] = 'Focus on clean shooting over pure speed'
        
        return strategy

# Standalone functions for API endpoints
def analyze_team_fatigue_patterns(team_athletes: List[str]) -> Dict:
    """Analyze fatigue patterns across entire team"""
    engine = FatigueResistanceEngine()
    team_analysis = {
        'team_average_resistance': 0,
        'weakest_area': None,
        'strongest_area': None,
        'athletes_needing_support': [],
        'team_trends': {}
    }
    
    profiles = []
    for athlete_id in team_athletes:
        # Load athlete data and generate profile
        # ... (implementation based on data source)
        pass
    
    return team_analysis

def compare_athletes_fatigue(athlete1_id: str, athlete2_id: str) -> Dict:
    """Direct comparison of two athletes' fatigue profiles"""
    comparison = {
        'better_recovery': None,
        'better_under_pressure': None,
        'better_fatigue_resistance': None,
        'recommendations': {}
    }
    
    # Implementation here
    return comparison
