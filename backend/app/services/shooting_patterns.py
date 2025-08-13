"""
Advanced Shooting Pattern Analysis
Based on research: 1st prone and 5th standing shots are most difficult
References: PMC12036221, arXiv:2411.02000v1
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from scipy import stats
import logging

logger = logging.getLogger(__name__)

@dataclass
class ShotPattern:
    """Individual shot within a shooting sequence"""
    shot_number: int  # 1-5
    hit: bool
    time_to_shot: float  # Seconds from previous shot
    heart_rate: int
    stability_score: float  # From shooting simulator
    wind_conditions: float
    pressure_level: str  # 'low', 'medium', 'high'

@dataclass 
class ShootingSequence:
    """Complete 5-shot sequence analysis"""
    race_id: str
    date: datetime
    position: str  # 'prone' or 'standing'
    sequence_number: int  # 1-4 in race
    
    shots: List[ShotPattern]
    total_time: float
    total_hits: int
    
    # Context
    race_position_before: int
    race_position_after: int
    competitors_nearby: int  # Within 10 seconds
    
    # Patterns detected
    has_first_shot_problem: bool
    has_last_shot_problem: bool
    rhythm_consistency: float  # 0-100
    
class ShootingPatternAnalyzer:
    """
    Analyzes shooting patterns to identify weaknesses and strengths
    Focus on shot-by-shot analysis within each sequence
    """
    
    def __init__(self):
        # Research-based problem shot positions
        self.PROBLEM_SHOTS = {
            'prone': [1],  # First shot most difficult
            'standing': [5]  # Last shot most difficult
        }
        
        # Ideal timing between shots (seconds)
        self.IDEAL_RHYTHM = {
            'prone': 4.5,
            'standing': 5.5
        }
    
    def analyze_shooting_patterns(
        self,
        athlete_id: str,
        shooting_history: List[Dict]
    ) -> Dict:
        """
        Complete shooting pattern analysis with historical comparison
        """
        
        # Parse shooting sequences
        sequences = self._parse_shooting_sequences(shooting_history)
        
        # Analyze patterns
        analysis = {
            'athlete_id': athlete_id,
            'total_sequences_analyzed': len(sequences),
            
            # Shot-by-shot accuracy
            'shot_accuracy_by_position': self._analyze_shot_positions(sequences),
            
            # Problem identification
            'problem_shots': self._identify_problem_shots(sequences),
            
            # Rhythm analysis
            'rhythm_analysis': self._analyze_shooting_rhythm(sequences),
            
            # Pressure analysis
            'pressure_patterns': self._analyze_pressure_patterns(sequences),
            
            # Historical trends
            'historical_trends': self._analyze_historical_patterns(sequences),
            
            # Position comparison
            'prone_vs_standing': self._compare_positions(sequences),
            
            # Recommendations
            'technical_recommendations': self._generate_recommendations(sequences)
        }
        
        return analysis
    
    def _analyze_shot_positions(self, sequences: List[ShootingSequence]) -> Dict:
        """Analyze accuracy for each shot position (1-5)"""
        position_stats = {
            'prone': {i: {'hits': 0, 'total': 0} for i in range(1, 6)},
            'standing': {i: {'hits': 0, 'total': 0} for i in range(1, 6)}
        }
        
        for seq in sequences:
            for i, shot in enumerate(seq.shots, 1):
                position_stats[seq.position][i]['total'] += 1
                if shot.hit:
                    position_stats[seq.position][i]['hits'] += 1
        
        # Calculate percentages
        result = {}
        for position in ['prone', 'standing']:
            result[position] = {}
            for shot_num in range(1, 6):
                stats = position_stats[position][shot_num]
                if stats['total'] > 0:
                    accuracy = (stats['hits'] / stats['total']) * 100
                    result[position][f'shot_{shot_num}_accuracy'] = accuracy
                    result[position][f'shot_{shot_num}_total'] = stats['total']
                    
                    # Flag problem shots
                    if accuracy < 80 and stats['total'] > 20:
                        logger.warning(f"Problem detected: {position} shot {shot_num} at {accuracy:.1f}%")
        
        return result
    
    def _identify_problem_shots(self, sequences: List[ShootingSequence]) -> Dict:
        """Identify specific shot positions causing problems"""
        problems = {
            'first_shot_syndrome': {'prone': False, 'standing': False},
            'last_shot_syndrome': {'prone': False, 'standing': False},
            'middle_shot_issues': [],
            'recommendations': []
        }
        
        # Analyze first shot issues
        for position in ['prone', 'standing']:
            pos_sequences = [s for s in sequences if s.position == position]
            if pos_sequences:
                first_shots = [s.shots[0].hit for s in pos_sequences if s.shots]
                if first_shots:
                    first_accuracy = sum(first_shots) / len(first_shots)
                    if first_accuracy < 0.75:
                        problems['first_shot_syndrome'][position] = True
                        problems['recommendations'].append(
                            f"Focus on {position} first shot setup - currently {first_accuracy*100:.1f}% accuracy"
                        )
        
        # Analyze last shot issues  
        for position in ['prone', 'standing']:
            pos_sequences = [s for s in sequences if s.position == position]
            if pos_sequences:
                last_shots = [s.shots[-1].hit for s in pos_sequences if len(s.shots) >= 5]
                if last_shots:
                    last_accuracy = sum(last_shots) / len(last_shots)
                    if last_accuracy < 0.75:
                        problems['last_shot_syndrome'][position] = True
                        problems['recommendations'].append(
                            f"Mental training for {position} 5th shot - currently {last_accuracy*100:.1f}% accuracy"
                        )
        
        return problems
    
    def _analyze_shooting_rhythm(self, sequences: List[ShootingSequence]) -> Dict:
        """Analyze timing consistency between shots"""
        rhythm_analysis = {
            'prone': {'avg_time_between_shots': 0, 'consistency_score': 0},
            'standing': {'avg_time_between_shots': 0, 'consistency_score': 0},
            'optimal_rhythm_found': {}
        }
        
        for position in ['prone', 'standing']:
            pos_sequences = [s for s in sequences if s.position == position]
            
            if not pos_sequences:
                continue
            
            # Calculate timing between shots
            all_timings = []
            successful_timings = []
            
            for seq in pos_sequences:
                for i in range(1, len(seq.shots)):
                    timing = seq.shots[i].time_to_shot
                    all_timings.append(timing)
                    
                    # Track timing for successful sequences
                    if seq.total_hits >= 4:
                        successful_timings.append(timing)
            
            if all_timings:
                avg_timing = np.mean(all_timings)
                timing_std = np.std(all_timings)
                
                # Consistency score (lower std = higher consistency)
                consistency = max(0, 100 - (timing_std * 20))
                
                rhythm_analysis[position] = {
                    'avg_time_between_shots': avg_timing,
                    'timing_std': timing_std,
                    'consistency_score': consistency
                }
                
                # Find optimal rhythm (timing in successful sequences)
                if successful_timings:
                    optimal_timing = np.mean(successful_timings)
                    rhythm_analysis['optimal_rhythm_found'][position] = optimal_timing
        
        return rhythm_analysis
    
    def _analyze_pressure_patterns(self, sequences: List[ShootingSequence]) -> Dict:
        """Analyze shooting under different pressure situations"""
        pressure_analysis = {
            'high_pressure_accuracy': 0,
            'low_pressure_accuracy': 0,
            'clutch_performance': 0,
            'choke_risk': 0
        }
        
        high_pressure_shots = []
        low_pressure_shots = []
        
        for seq in sequences:
            # Define pressure based on race context
            is_high_pressure = (
                seq.sequence_number >= 3 or  # Last shootings
                seq.race_position_before <= 10 or  # Leading
                seq.competitors_nearby >= 3  # Pack shooting
            )
            
            for shot in seq.shots:
                if is_high_pressure:
                    high_pressure_shots.append(shot.hit)
                else:
                    low_pressure_shots.append(shot.hit)
        
        if high_pressure_shots:
            pressure_analysis['high_pressure_accuracy'] = sum(high_pressure_shots) / len(high_pressure_shots) * 100
        
        if low_pressure_shots:
            pressure_analysis['low_pressure_accuracy'] = sum(low_pressure_shots) / len(low_pressure_shots) * 100
        
        # Calculate clutch performance
        if high_pressure_shots and low_pressure_shots:
            clutch = pressure_analysis['high_pressure_accuracy'] / pressure_analysis['low_pressure_accuracy']
            pressure_analysis['clutch_performance'] = min(100, clutch * 100)
            
            # Choke risk (significant drop under pressure)
            if clutch < 0.85:
                pressure_analysis['choke_risk'] = (1 - clutch) * 100
        
        return pressure_analysis
    
    def _analyze_historical_patterns(self, sequences: List[ShootingSequence]) -> Dict:
        """Analyze how patterns evolved over time"""
        if len(sequences) < 20:
            return {'status': 'insufficient_data'}
        
        # Sort by date
        sorted_seq = sorted(sequences, key=lambda x: x.date)
        
        # Split into periods
        third = len(sorted_seq) // 3
        early = sorted_seq[:third]
        middle = sorted_seq[third:2*third]
        recent = sorted_seq[2*third:]
        
        trends = {
            'accuracy_trend': [],
            'rhythm_improvement': [],
            'pressure_handling_evolution': []
        }
        
        # Calculate metrics for each period
        for period_name, period_seqs in [('early', early), ('middle', middle), ('recent', recent)]:
            if period_seqs:
                # Accuracy
                total_hits = sum(s.total_hits for s in period_seqs)
                total_shots = len(period_seqs) * 5
                accuracy = (total_hits / total_shots) * 100 if total_shots > 0 else 0
                
                trends['accuracy_trend'].append({
                    'period': period_name,
                    'accuracy': accuracy,
                    'sample_size': len(period_seqs)
                })
        
        # Determine overall trend
        if len(trends['accuracy_trend']) >= 3:
            early_acc = trends['accuracy_trend'][0]['accuracy']
            recent_acc = trends['accuracy_trend'][2]['accuracy']
            
            if recent_acc > early_acc + 5:
                trends['direction'] = 'improving'
            elif recent_acc < early_acc - 5:
                trends['direction'] = 'declining'
            else:
                trends['direction'] = 'stable'
            
            trends['total_improvement'] = recent_acc - early_acc
        
        return trends
    
    def _compare_positions(self, sequences: List[ShootingSequence]) -> Dict:
        """Compare prone vs standing performance"""
        prone_seqs = [s for s in sequences if s.position == 'prone']
        standing_seqs = [s for s in sequences if s.position == 'standing']
        
        comparison = {}
        
        if prone_seqs:
            prone_hits = sum(s.total_hits for s in prone_seqs)
            prone_total = len(prone_seqs) * 5
            comparison['prone_accuracy'] = (prone_hits / prone_total) * 100
            comparison['prone_avg_time'] = np.mean([s.total_time for s in prone_seqs])
        
        if standing_seqs:
            standing_hits = sum(s.total_hits for s in standing_seqs)
            standing_total = len(standing_seqs) * 5
            comparison['standing_accuracy'] = (standing_hits / standing_total) * 100
            comparison['standing_avg_time'] = np.mean([s.total_time for s in standing_seqs])
        
        if 'prone_accuracy' in comparison and 'standing_accuracy' in comparison:
            comparison['position_gap'] = comparison['prone_accuracy'] - comparison['standing_accuracy']
            
            if comparison['position_gap'] > 10:
                comparison['weakness'] = 'standing'
                comparison['recommendation'] = 'Significant standing shooting weakness - prioritize standing stability training'
            elif comparison['position_gap'] < -5:
                comparison['weakness'] = 'prone'
                comparison['recommendation'] = 'Unusual prone weakness - check rifle setup and position'
            else:
                comparison['weakness'] = 'balanced'
                comparison['recommendation'] = 'Good balance between positions'
        
        return comparison
    
    def _generate_recommendations(self, sequences: List[ShootingSequence]) -> List[Dict]:
        """Generate specific training recommendations"""
        recommendations = []
        
        # Analyze all the patterns
        shot_accuracy = self._analyze_shot_positions(sequences)
        problems = self._identify_problem_shots(sequences)
        rhythm = self._analyze_shooting_rhythm(sequences)
        pressure = self._analyze_pressure_patterns(sequences)
        
        # First shot problems
        if problems['first_shot_syndrome']['prone'] or problems['first_shot_syndrome']['standing']:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'First Shot Setup',
                'drills': [
                    'Cold bore shooting practice',
                    'Single shot drills with full setup',
                    'Breathing pattern establishment',
                    'Mental routine for first shot confidence'
                ]
            })
        
        # Rhythm issues
        for position in ['prone', 'standing']:
            if position in rhythm and rhythm[position]['consistency_score'] < 70:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'area': f'{position.capitalize()} Rhythm',
                    'issue': f'Inconsistent timing (score: {rhythm[position]["consistency_score"]:.0f}/100)',
                    'drills': [
                        f'Metronome training at {rhythm.get("optimal_rhythm_found", {}).get(position, 5):.1f}s',
                        'Dry fire rhythm practice',
                        'Video analysis of shot timing'
                    ]
                })
        
        # Pressure handling
        if pressure['choke_risk'] > 15:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Pressure Management',
                'issue': f'Performance drops {pressure["choke_risk"]:.0f}% under pressure',
                'drills': [
                    'Competition simulation training',
                    'Breathing exercises for stress management',
                    'Progressive pressure training',
                    'Visualization of clutch situations'
                ]
            })
        
        return recommendations
    
    def _parse_shooting_sequences(self, shooting_history: List[Dict]) -> List[ShootingSequence]:
        """Parse raw data into ShootingSequence objects"""
        sequences = []
        
        for race_data in shooting_history:
            for shooting in race_data.get('shootings', []):
                # Create shot patterns
                shots = []
                for i, hit in enumerate(shooting.get('hits_pattern', [])):
                    shot = ShotPattern(
                        shot_number=i + 1,
                        hit=hit,
                        time_to_shot=shooting.get('shot_times', [5] * 5)[i],
                        heart_rate=shooting.get('hr_during_shots', [140] * 5)[i],
                        stability_score=shooting.get('stability_scores', [80] * 5)[i],
                        wind_conditions=race_data.get('wind_speed', 0),
                        pressure_level=shooting.get('pressure_level', 'medium')
                    )
                    shots.append(shot)
                
                # Create sequence
                seq = ShootingSequence(
                    race_id=race_data.get('race_id', ''),
                    date=datetime.fromisoformat(race_data.get('date', datetime.now().isoformat())),
                    position=shooting.get('position', 'prone'),
                    sequence_number=shooting.get('sequence', 1),
                    shots=shots,
                    total_time=shooting.get('total_time', 30),
                    total_hits=sum(s.hit for s in shots),
                    race_position_before=shooting.get('position_before', 30),
                    race_position_after=shooting.get('position_after', 30),
                    competitors_nearby=shooting.get('competitors_nearby', 0),
                    has_first_shot_problem=not shots[0].hit if shots else False,
                    has_last_shot_problem=not shots[-1].hit if len(shots) >= 5 else False,
                    rhythm_consistency=self._calculate_rhythm_consistency(shots)
                )
                sequences.append(seq)
        
        return sequences
    
    def _calculate_rhythm_consistency(self, shots: List[ShotPattern]) -> float:
        """Calculate rhythm consistency score for a sequence"""
        if len(shots) < 2:
            return 50.0
        
        timings = [shot.time_to_shot for shot in shots[1:]]
        if timings:
            std_dev = np.std(timings)
            # Convert to 0-100 score (lower std = higher score)
            consistency = max(0, 100 - (std_dev * 25))
            return consistency
        
        return 50.0

def generate_shooting_report(athlete_id: str, season: str = '2024-25') -> Dict:
    """Generate comprehensive shooting report for athlete"""
    analyzer = ShootingPatternAnalyzer()
    
    # Load shooting history (implement based on data source)
    # shooting_history = load_athlete_shooting_data(athlete_id, season)
    
    # Run analysis
    # analysis = analyzer.analyze_shooting_patterns(athlete_id, shooting_history)
    
    # Format for report
    report = {
        'athlete_id': athlete_id,
        'season': season,
        'generated_at': datetime.now().isoformat(),
        # 'analysis': analysis,
        'executive_summary': 'Generated shooting pattern analysis'
    }
    
    return report
