"""
Digital Twin Engine - Complete Physiological Model of Athletes
Enables what-if scenarios and race simulations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from scipy import stats, optimize
from sklearn.ensemble import RandomForestRegressor
import json

logger = logging.getLogger(__name__)

@dataclass
class PhysiologicalModel:
    """Complete physiological model of an athlete"""
    
    # Basic parameters
    athlete_id: str
    name: str
    age: int
    weight: float  # kg
    height: float  # cm
    
    # Aerobic capacity
    vo2_max: float  # ml/kg/min
    lactate_threshold: float  # % of VO2max
    anaerobic_threshold: float  # % of VO2max
    
    # Heart rate zones
    hr_max: int
    hr_rest: int
    hr_zones: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    
    # Shooting parameters
    optimal_shooting_hr: int
    hr_recovery_rate: float  # bpm/second
    shooting_accuracy_curve: Dict[int, float] = field(default_factory=dict)
    
    # Fatigue parameters
    fatigue_accumulation_rate: float
    fatigue_recovery_rate: float
    lactate_clearance_rate: float
    
    # Mental parameters
    pressure_resistance: float  # 0-1
    focus_duration: float  # seconds
    stress_recovery: float  # 0-1
    
    # Technical skills
    ski_efficiency: float  # 0-1
    shooting_technique: float  # 0-1
    transition_speed: float  # seconds
    
    def __post_init__(self):
        """Calculate derived parameters"""
        if not self.hr_zones:
            self.calculate_hr_zones()
        if not self.shooting_accuracy_curve:
            self.generate_shooting_curve()
    
    def calculate_hr_zones(self):
        """Calculate training zones based on HR max"""
        self.hr_zones = {
            'Z1': (self.hr_rest, int(self.hr_max * 0.6)),  # Recovery
            'Z2': (int(self.hr_max * 0.6), int(self.hr_max * 0.7)),  # Aerobic
            'Z3': (int(self.hr_max * 0.7), int(self.hr_max * 0.8)),  # Threshold
            'Z4': (int(self.hr_max * 0.8), int(self.hr_max * 0.9)),  # VO2max
            'Z5': (int(self.hr_max * 0.9), self.hr_max)  # Neuromuscular
        }
    
    def generate_shooting_curve(self):
        """Generate shooting accuracy based on HR"""
        for hr in range(100, 200, 5):
            # Accuracy drops as HR increases
            if hr <= self.optimal_shooting_hr:
                accuracy = 0.95 - (self.optimal_shooting_hr - hr) * 0.001
            else:
                # Steeper drop after optimal HR
                accuracy = 0.95 - (hr - self.optimal_shooting_hr) * 0.003
            
            # Apply technique modifier
            accuracy *= self.shooting_technique
            
            # Ensure bounds
            self.shooting_accuracy_curve[hr] = max(0.5, min(1.0, accuracy))

@dataclass
class RaceSimulation:
    """Simulated race with all parameters"""
    
    race_type: str  # sprint, pursuit, individual, mass_start
    distance: float  # km
    laps: int
    shootings: List[str]  # ['prone', 'prone', 'standing', 'standing']
    
    # Environmental conditions
    temperature: float  # celsius
    altitude: int  # meters
    wind_speed: float  # m/s
    snow_condition: str  # hard, soft, wet
    
    # Race dynamics
    start_position: int = 1
    competitors: int = 30
    
    def get_penalty_loop_distance(self) -> float:
        """Get penalty loop distance based on race type"""
        return 0.15 if self.race_type in ['sprint', 'pursuit'] else 0.0

class DigitalTwinEngine:
    """Main engine for athlete digital twins"""
    
    def __init__(self):
        self.twins: Dict[str, PhysiologicalModel] = {}
        self.simulations: List[Dict] = []
        
    def create_twin(self, athlete_data: Dict) -> PhysiologicalModel:
        """Create digital twin from athlete data"""
        
        # Extract basic info
        athlete_id = athlete_data.get('id')
        name = athlete_data.get('name', 'Unknown')
        
        # Estimate physiological parameters from performance
        world_rank = int(athlete_data.get('world_rank', 50))
        
        # Elite athletes have better parameters
        base_vo2 = 70 - world_rank * 0.3  # Elite ~65-70
        
        twin = PhysiologicalModel(
            athlete_id=athlete_id,
            name=name,
            age=athlete_data.get('age', 25),
            weight=athlete_data.get('weight', 60),
            height=athlete_data.get('height', 170),
            
            # Aerobic capacity (estimated from rank)
            vo2_max=max(45, min(75, base_vo2 + np.random.normal(0, 2))),
            lactate_threshold=0.75 + (50 - world_rank) * 0.002,
            anaerobic_threshold=0.85 + (50 - world_rank) * 0.001,
            
            # HR parameters
            hr_max=195 - int(athlete_data.get('age', 25) * 0.5),
            hr_rest=45 + np.random.randint(-5, 5),
            optimal_shooting_hr=155 + np.random.randint(-10, 10),
            hr_recovery_rate=1.2 + (50 - world_rank) * 0.01,
            
            # Fatigue parameters
            fatigue_accumulation_rate=0.02 + world_rank * 0.0005,
            fatigue_recovery_rate=0.03 + (50 - world_rank) * 0.0005,
            lactate_clearance_rate=0.025 + (50 - world_rank) * 0.0003,
            
            # Mental parameters
            pressure_resistance=0.8 - world_rank * 0.005,
            focus_duration=30 + (50 - world_rank) * 0.5,
            stress_recovery=0.7 + (50 - world_rank) * 0.003,
            
            # Technical skills
            ski_efficiency=0.9 - world_rank * 0.003,
            shooting_technique=0.85 - world_rank * 0.002,
            transition_speed=25 + world_rank * 0.2
        )
        
        self.twins[athlete_id] = twin
        return twin
    
    def simulate_race(self, 
                     twin: PhysiologicalModel, 
                     race: RaceSimulation,
                     strategy: Optional[Dict] = None) -> Dict:
        """Simulate complete race for athlete"""
        
        if strategy is None:
            strategy = self.get_optimal_strategy(twin, race)
        
        # Initialize race state
        state = {
            'time': 0,
            'distance': 0,
            'hr': twin.hr_rest + 50,  # Start HR
            'lactate': 2.0,  # mmol/L
            'fatigue': 0,
            'shots_fired': 0,
            'misses': 0,
            'lap': 1,
            'position': race.start_position,
            'segments': []
        }
        
        # Simulate each lap
        for lap in range(1, race.laps + 1):
            lap_result = self.simulate_lap(twin, race, state, strategy, lap)
            state.update(lap_result)
            
            # Shooting after each lap except last
            if lap < race.laps:
                shooting_position = 'prone' if lap <= 2 else 'standing'
                shooting_result = self.simulate_shooting(
                    twin, state, shooting_position, race
                )
                state.update(shooting_result)
                
                # Add penalty loops
                if shooting_result['misses'] > 0:
                    penalty_time = self.simulate_penalty_loops(
                        twin, state, shooting_result['misses'], race
                    )
                    state['time'] += penalty_time
        
        # Calculate final metrics
        result = {
            'athlete_id': twin.athlete_id,
            'name': twin.name,
            'race_type': race.race_type,
            'total_time': state['time'],
            'ski_time': state.get('ski_time', state['time'] - state.get('shooting_time', 0)),
            'shooting_time': state.get('shooting_time', 0),
            'total_misses': state['misses'],
            'final_position': self.calculate_final_position(state, race),
            'avg_hr': state.get('avg_hr', 0),
            'max_hr': state.get('max_hr', twin.hr_max),
            'fatigue_level': state['fatigue'],
            'segments': state['segments']
        }
        
        return result
    
    def simulate_lap(self, twin: PhysiologicalModel, race: RaceSimulation, 
                    state: Dict, strategy: Dict, lap_number: int) -> Dict:
        """Simulate one lap of skiing"""
        
        lap_distance = race.distance / race.laps
        
        # Determine intensity based on strategy
        target_intensity = strategy.get(f'lap_{lap_number}_intensity', 0.8)
        
        # Adjust for fatigue
        actual_intensity = target_intensity * (1 - state['fatigue'] * 0.2)
        
        # Calculate speed (km/h)
        base_speed = 25 * twin.ski_efficiency * actual_intensity
        
        # Environmental adjustments
        altitude_factor = 1 - (race.altitude / 10000) * 0.05
        temp_factor = 1 - abs(race.temperature + 5) * 0.001
        wind_factor = 1 - race.wind_speed * 0.01
        
        actual_speed = base_speed * altitude_factor * temp_factor * wind_factor
        
        # Calculate lap time
        lap_time = (lap_distance / actual_speed) * 3600  # seconds
        
        # Update physiological state
        avg_hr = twin.hr_max * actual_intensity
        lactate_production = 2 + actual_intensity * 10
        lactate_clearance = twin.lactate_clearance_rate * lap_time
        
        new_lactate = state['lactate'] + lactate_production - lactate_clearance
        new_fatigue = min(1.0, state['fatigue'] + twin.fatigue_accumulation_rate * actual_intensity)
        
        segment = {
            'type': 'ski',
            'lap': lap_number,
            'distance': lap_distance,
            'time': lap_time,
            'speed': actual_speed,
            'hr': avg_hr,
            'intensity': actual_intensity
        }
        
        return {
            'time': state['time'] + lap_time,
            'distance': state['distance'] + lap_distance,
            'hr': avg_hr,
            'lactate': max(1.0, new_lactate),
            'fatigue': new_fatigue,
            'ski_time': state.get('ski_time', 0) + lap_time,
            'segments': state['segments'] + [segment]
        }
    
    def simulate_shooting(self, twin: PhysiologicalModel, state: Dict, 
                         position: str, race: RaceSimulation) -> Dict:
        """Simulate shooting with 5 targets"""
        
        arrival_hr = state['hr']
        
        # Time to prepare and shoot
        prep_time = twin.transition_speed
        
        # HR recovery during prep
        recovery_time = prep_time
        recovered_hr = arrival_hr - (twin.hr_recovery_rate * recovery_time)
        shooting_hr = max(twin.hr_rest + 20, recovered_hr)
        
        # Get base accuracy from HR curve
        hr_key = round(shooting_hr / 5) * 5  # Round to nearest 5
        base_accuracy = twin.shooting_accuracy_curve.get(hr_key, 0.8)
        
        # Adjust for position
        if position == 'standing':
            base_accuracy *= 0.9  # Standing is harder
        
        # Adjust for fatigue
        fatigue_penalty = state['fatigue'] * 0.15
        base_accuracy *= (1 - fatigue_penalty)
        
        # Adjust for wind
        wind_penalty = min(0.2, race.wind_speed * 0.02)
        base_accuracy *= (1 - wind_penalty)
        
        # Shoot 5 targets
        hits = 0
        shooting_pattern = []
        
        for shot in range(5):
            # Add pressure for last shot
            shot_accuracy = base_accuracy
            if shot == 4:  # Last shot
                shot_accuracy *= twin.pressure_resistance
            
            # Random shot with accuracy probability
            if np.random.random() < shot_accuracy:
                hits += 1
                shooting_pattern.append(1)
            else:
                shooting_pattern.append(0)
        
        misses = 5 - hits
        shooting_time = prep_time + 3 * 5  # ~3 seconds per shot
        
        segment = {
            'type': 'shooting',
            'position': position,
            'arrival_hr': arrival_hr,
            'shooting_hr': shooting_hr,
            'hits': hits,
            'misses': misses,
            'pattern': shooting_pattern,
            'time': shooting_time,
            'accuracy': hits / 5 * 100
        }
        
        return {
            'time': state['time'] + shooting_time,
            'misses': state['misses'] + misses,
            'shots_fired': state['shots_fired'] + 5,
            'shooting_time': state.get('shooting_time', 0) + shooting_time,
            'segments': state['segments'] + [segment]
        }
    
    def simulate_penalty_loops(self, twin: PhysiologicalModel, state: Dict, 
                              misses: int, race: RaceSimulation) -> float:
        """Calculate penalty loop time"""
        
        loop_distance = race.get_penalty_loop_distance()
        
        if loop_distance == 0:  # Individual race - time penalty
            return misses * 60  # 1 minute per miss
        
        # Sprint/Pursuit - ski penalty loops
        loop_speed = 20 * twin.ski_efficiency * (1 - state['fatigue'] * 0.3)
        loop_time = (loop_distance / loop_speed) * 3600  # seconds
        
        return misses * loop_time
    
    def calculate_final_position(self, state: Dict, race: RaceSimulation) -> int:
        """Estimate final position based on time"""
        
        # Simple model - each 30 seconds ~ 1 position
        time_behind_winner = max(0, state['time'] - self.get_winning_time(race))
        positions_lost = int(time_behind_winner / 30)
        
        return min(race.competitors, race.start_position + positions_lost)
    
    def get_winning_time(self, race: RaceSimulation) -> float:
        """Get expected winning time for race"""
        
        times = {
            'sprint': {'M': 1320, 'W': 1200},  # 22min, 20min
            'pursuit': {'M': 1980, 'W': 1800},  # 33min, 30min
            'individual': {'M': 2880, 'W': 2400},  # 48min, 40min
            'mass_start': {'M': 2100, 'W': 1920}  # 35min, 32min
        }
        
        return times.get(race.race_type, {}).get('W', 1500)
    
    def get_optimal_strategy(self, twin: PhysiologicalModel, 
                           race: RaceSimulation) -> Dict:
        """Calculate optimal pacing strategy"""
        
        strategy = {}
        
        # Base intensity on VO2max and lactate threshold
        threshold_intensity = twin.lactate_threshold
        
        if race.race_type == 'sprint':
            # Higher intensity for shorter race
            for lap in range(1, race.laps + 1):
                if lap == 1:
                    strategy[f'lap_{lap}_intensity'] = threshold_intensity * 0.95
                elif lap == race.laps:
                    strategy[f'lap_{lap}_intensity'] = threshold_intensity * 1.05
                else:
                    strategy[f'lap_{lap}_intensity'] = threshold_intensity
                    
        elif race.race_type == 'individual':
            # Conservative pacing for long race
            for lap in range(1, race.laps + 1):
                strategy[f'lap_{lap}_intensity'] = threshold_intensity * 0.9
                
        else:  # pursuit, mass_start
            # Tactical pacing
            for lap in range(1, race.laps + 1):
                if lap <= 2:
                    strategy[f'lap_{lap}_intensity'] = threshold_intensity * 0.92
                else:
                    strategy[f'lap_{lap}_intensity'] = threshold_intensity * 0.98
        
        return strategy
    
    def run_what_if_scenario(self, athlete_id: str, scenario: Dict) -> Dict:
        """Run what-if analysis"""
        
        if athlete_id not in self.twins:
            raise ValueError(f"No digital twin for athlete {athlete_id}")
        
        twin = self.twins[athlete_id]
        
        # Create modified twin based on scenario
        modified_twin = self.modify_twin(twin, scenario.get('modifications', {}))
        
        # Setup race
        race = RaceSimulation(
            race_type=scenario.get('race_type', 'sprint'),
            distance=scenario.get('distance', 7.5),
            laps=scenario.get('laps', 3),
            shootings=scenario.get('shootings', ['prone', 'prone', 'standing', 'standing']),
            temperature=scenario.get('temperature', -5),
            altitude=scenario.get('altitude', 500),
            wind_speed=scenario.get('wind_speed', 2),
            snow_condition=scenario.get('snow', 'hard')
        )
        
        # Run baseline simulation
        baseline = self.simulate_race(twin, race)
        
        # Run modified simulation
        modified = self.simulate_race(modified_twin, race)
        
        # Calculate improvements
        improvement = {
            'time_saved': baseline['total_time'] - modified['total_time'],
            'positions_gained': baseline['final_position'] - modified['final_position'],
            'shooting_improvement': baseline['total_misses'] - modified['total_misses'],
            'baseline': baseline,
            'modified': modified,
            'scenario': scenario
        }
        
        return improvement
    
    def modify_twin(self, twin: PhysiologicalModel, modifications: Dict) -> PhysiologicalModel:
        """Create modified version of twin"""
        
        import copy
        modified = copy.deepcopy(twin)
        
        for param, value in modifications.items():
            if hasattr(modified, param):
                if 'percent' in str(value):
                    # Percentage change
                    current = getattr(modified, param)
                    change = float(value.replace('percent', '').replace('+', '')) / 100
                    setattr(modified, param, current * (1 + change))
                else:
                    # Absolute value
                    setattr(modified, param, value)
        
        # Recalculate derived parameters
        modified.calculate_hr_zones()
        modified.generate_shooting_curve()
        
        return modified
    
    def generate_training_plan(self, athlete_id: str, goals: Dict) -> Dict:
        """Generate personalized training plan based on digital twin"""
        
        if athlete_id not in self.twins:
            raise ValueError(f"No digital twin for athlete {athlete_id}")
        
        twin = self.twins[athlete_id]
        plan = {
            'athlete': twin.name,
            'duration_weeks': goals.get('weeks', 8),
            'focus_areas': [],
            'weekly_schedule': [],
            'expected_improvements': {}
        }
        
        # Identify weaknesses
        weaknesses = []
        
        if twin.vo2_max < 60:
            weaknesses.append('aerobic_capacity')
        if twin.shooting_technique < 0.85:
            weaknesses.append('shooting_technique')
        if twin.pressure_resistance < 0.75:
            weaknesses.append('mental_training')
        if twin.ski_efficiency < 0.85:
            weaknesses.append('ski_technique')
        
        # Generate weekly plan
        for week in range(1, plan['duration_weeks'] + 1):
            week_plan = {
                'week': week,
                'total_hours': 15 + week * 0.5,
                'sessions': []
            }
            
            # Progressive overload
            if 'aerobic_capacity' in weaknesses:
                week_plan['sessions'].append({
                    'type': 'Z2_ski',
                    'duration': 90 + week * 5,
                    'frequency': 3,
                    'intensity': 'aerobic'
                })
                week_plan['sessions'].append({
                    'type': 'intervals',
                    'duration': 60,
                    'frequency': 2,
                    'intensity': f'{80 + week}% VO2max'
                })
            
            if 'shooting_technique' in weaknesses:
                week_plan['sessions'].append({
                    'type': 'dry_fire',
                    'duration': 45,
                    'frequency': 5,
                    'focus': 'technique'
                })
                week_plan['sessions'].append({
                    'type': 'combo_training',
                    'duration': 90,
                    'frequency': 2,
                    'focus': 'shooting_under_fatigue'
                })
            
            if 'mental_training' in weaknesses:
                week_plan['sessions'].append({
                    'type': 'visualization',
                    'duration': 20,
                    'frequency': 7,
                    'focus': 'race_simulation'
                })
            
            plan['weekly_schedule'].append(week_plan)
        
        # Expected improvements
        plan['expected_improvements'] = {
            'vo2_max': '+3-5%',
            'shooting_accuracy': '+8-12%',
            'race_time': '-45-90 seconds',
            'world_ranking': '-5-10 positions'
        }
        
        return plan

# API Endpoints
digital_twin_engine = DigitalTwinEngine()

def create_athlete_twin(athlete_id: str, athlete_data: Dict) -> Dict:
    """Create digital twin for athlete"""
    twin = digital_twin_engine.create_twin(athlete_data)
    return {
        'athlete_id': twin.athlete_id,
        'name': twin.name,
        'physiological_params': {
            'vo2_max': twin.vo2_max,
            'lactate_threshold': twin.lactate_threshold,
            'hr_max': twin.hr_max,
            'optimal_shooting_hr': twin.optimal_shooting_hr
        },
        'technical_skills': {
            'ski_efficiency': twin.ski_efficiency,
            'shooting_technique': twin.shooting_technique,
            'pressure_resistance': twin.pressure_resistance
        },
        'status': 'created'
    }

def simulate_race_scenario(athlete_id: str, race_params: Dict) -> Dict:
    """Simulate race for athlete"""
    
    if athlete_id not in digital_twin_engine.twins:
        # Create twin first
        digital_twin_engine.create_twin({'id': athlete_id, 'name': 'Athlete'})
    
    twin = digital_twin_engine.twins[athlete_id]
    
    race = RaceSimulation(
        race_type=race_params.get('type', 'sprint'),
        distance=race_params.get('distance', 7.5),
        laps=race_params.get('laps', 3),
        shootings=race_params.get('shootings', ['prone', 'prone', 'standing', 'standing']),
        temperature=race_params.get('temperature', -5),
        altitude=race_params.get('altitude', 500),
        wind_speed=race_params.get('wind_speed', 2),
        snow_condition=race_params.get('snow', 'hard')
    )
    
    result = digital_twin_engine.simulate_race(twin, race)
    return result

def analyze_what_if(athlete_id: str, scenario: Dict) -> Dict:
    """Run what-if analysis"""
    return digital_twin_engine.run_what_if_scenario(athlete_id, scenario)

def generate_optimal_training(athlete_id: str, goals: Dict) -> Dict:
    """Generate optimal training plan"""
    return digital_twin_engine.generate_training_plan(athlete_id, goals)
