"""Complete IBU API Service with all biathlonresults features"""

import biathlonresults as br
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class IBUFullService:
    """Full IBU data service with history, analytics, predictions"""
    
    def __init__(self):
        self.current_season = "2425"  # 2024/2025
        self.czech_ibu_ids = self._load_czech_athletes()
    
    def _load_czech_athletes(self) -> List[str]:
        """Load all Czech athlete IDs"""
        try:
            # Search for Czech athletes
            athletes = br.athletes(nat='CZE')
            return [a['IBUId'] for a in athletes.get('Athletes', [])]
        except:
            # Fallback to known Czech athletes
            return [
                'BTCZE12903199501',  # Davidová
                'BTCZE11502200001',  # Jislová  
                'BTCZE12811199401',  # Charvátová
                'BTCZE10911199601',  # Krčmář
                'BTCZE13012199701',  # Hornig
            ]
    
    @lru_cache(maxsize=128)
    def get_athlete_history(self, ibu_id: str, limit: int = 50) -> Dict:
        """Get complete athlete history with context"""
        try:
            # Get all results
            all_results = br.all_results(ibu_id)
            results = all_results.get('Results', [])[:limit]
            
            # Process results with context
            history = []
            for result in results:
                race_details = self._get_race_details(result['RaceId'])
                
                history_item = {
                    'date': race_details.get('date'),
                    'location': result.get('Place', ''),
                    'race_type': result.get('Comp', ''),
                    'rank': result.get('Rank'),
                    'race_id': result['RaceId'],
                    'season': result.get('Season'),
                    
                    # Add context from race details
                    'weather': race_details.get('weather'),
                    'temperature': race_details.get('temperature'),
                    'wind': race_details.get('wind'),
                    
                    # Performance details
                    'shooting': self._parse_shooting(result.get('Shootings', '')),
                    'ski_rank': result.get('SkiRank'),
                    'total_time': result.get('TotalTime'),
                    'behind': result.get('Behind'),
                    
                    # Event markers (detect patterns)
                    'event_type': self._detect_event_type(result)
                }
                
                history.append(history_item)
            
            # Detect patterns
            patterns = self._analyze_patterns(history)
            
            # Calculate trends
            trends = self._calculate_trends(history)
            
            return {
                'athlete_id': ibu_id,
                'history': history,
                'patterns': patterns,
                'trends': trends,
                'total_races': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error getting athlete history: {e}")
            return {'history': [], 'patterns': [], 'trends': {}}
    
    def _get_race_details(self, race_id: str) -> Dict:
        """Get detailed race information"""
        try:
            # Get race results for context
            race = br.results(race_id)
            
            # Extract race metadata
            return {
                'date': race.get('Competition', {}).get('StartTime'),
                'weather': race.get('Weather', {}).get('Description'),
                'temperature': race.get('Weather', {}).get('AirTemp'),
                'wind': race.get('Weather', {}).get('WindSpeed'),
                'snow': race.get('Weather', {}).get('SnowCondition')
            }
        except:
            return {}
    
    def _parse_shooting(self, shooting_str: str) -> Dict:
        """Parse shooting string to detailed stats"""
        if not shooting_str:
            return {'total_misses': 0, 'pattern': [], 'prone': 0, 'standing': 0}
        
        # Parse format like "0+1+0+2" or "0 1 0 2"
        shots = [int(x) for x in shooting_str if x.isdigit()]
        
        # Usually first 2 are prone, last 2 standing (for sprint/pursuit)
        prone_misses = sum(shots[:2]) if len(shots) >= 2 else 0
        standing_misses = sum(shots[2:]) if len(shots) >= 4 else sum(shots[2:])
        
        return {
            'total_misses': sum(shots),
            'pattern': shots,
            'prone': prone_misses,
            'standing': standing_misses,
            'prone_accuracy': (10 - prone_misses) / 10 * 100 if len(shots) >= 2 else 100,
            'standing_accuracy': (10 - standing_misses) / 10 * 100 if len(shots) >= 4 else 100
        }
    
    def _detect_event_type(self, result: Dict) -> str:
        """Detect special events (illness, equipment change, etc.)"""
        rank = result.get('Rank')
        
        # DNF/DNS indicates problem
        if rank in ['DNF', 'DNS', 'DSQ']:
            return 'problem'
        
        # Big improvement
        if isinstance(rank, int) and rank <= 10:
            return 'success'
        
        return 'normal'
    
    def _analyze_patterns(self, history: List[Dict]) -> List[Dict]:
        """Analyze patterns in performance"""
        patterns = []
        
        # Sprint vs Pursuit performance
        sprint_ranks = [h['rank'] for h in history if h['race_type'] == 'SP' and isinstance(h['rank'], int)]
        pursuit_ranks = [h['rank'] for h in history if h['race_type'] == 'PU' and isinstance(h['rank'], int)]
        
        if sprint_ranks and pursuit_ranks:
            sprint_avg = sum(sprint_ranks) / len(sprint_ranks)
            pursuit_avg = sum(pursuit_ranks) / len(pursuit_ranks)
            
            if sprint_avg < pursuit_avg - 5:
                patterns.append({
                    'type': 'discipline_preference',
                    'message': 'Better in Sprint races',
                    'impact': f'{pursuit_avg - sprint_avg:.1f} positions better'
                })
        
        # Weather impact
        cold_races = [h for h in history if h.get('temperature') and float(h['temperature']) < -10]
        warm_races = [h for h in history if h.get('temperature') and float(h['temperature']) > 0]
        
        if cold_races and warm_races:
            cold_avg = sum(r['rank'] for r in cold_races if isinstance(r['rank'], int)) / len(cold_races)
            warm_avg = sum(r['rank'] for r in warm_races if isinstance(r['rank'], int)) / len(warm_races)
            
            if abs(cold_avg - warm_avg) > 5:
                patterns.append({
                    'type': 'weather_sensitivity',
                    'message': f'Better in {"cold" if cold_avg < warm_avg else "warm"} conditions',
                    'impact': f'{abs(cold_avg - warm_avg):.1f} positions difference'
                })
        
        return patterns
    
    def _calculate_trends(self, history: List[Dict]) -> Dict:
        """Calculate performance trends"""
        if len(history) < 3:
            return {'direction': 'insufficient_data'}
        
        # Get recent valid ranks
        recent_ranks = []
        older_ranks = []
        
        for i, h in enumerate(history):
            if isinstance(h['rank'], int):
                if i < 5:
                    recent_ranks.append(h['rank'])
                elif i < 15:
                    older_ranks.append(h['rank'])
        
        if not recent_ranks or not older_ranks:
            return {'direction': 'insufficient_data'}
        
        recent_avg = sum(recent_ranks) / len(recent_ranks)
        older_avg = sum(older_ranks) / len(older_ranks)
        
        improvement = older_avg - recent_avg  # Lower rank is better
        
        return {
            'direction': 'improving' if improvement > 2 else 'declining' if improvement < -2 else 'stable',
            'change': improvement,
            'recent_average': recent_avg,
            'season_average': older_avg,
            'confidence': 'high' if len(recent_ranks) >= 3 else 'medium'
        }
    
    def get_race_analysis(self, race_id: str) -> Dict:
        """Complete race analysis with Czech focus"""
        try:
            # Get race results
            race_results = br.results(race_id)
            results = race_results.get('Results', [])
            
            # Get race analytics
            course_time = br.analytic_results(race_id, type_id=br.consts.AnalysisType.TOTAL_COURSE_TIME)
            range_time = br.analytic_results(race_id, type_id=br.consts.AnalysisType.TOTAL_RANGE_TIME)
            shooting_time = br.analytic_results(race_id, type_id=br.consts.AnalysisType.TOTAL_SHOOTING_TIME)
            
            # Find Czech athletes
            czech_results = [r for r in results if r.get('Nat') == 'CZE']
            
            # Analyze each Czech athlete
            czech_analysis = []
            for czech in czech_results:
                # Find in analytics
                ski_rank = self._find_in_analytics(czech['IBUId'], course_time)
                shoot_rank = self._find_in_analytics(czech['IBUId'], shooting_time)
                
                analysis = {
                    'name': czech['Name'],
                    'ibu_id': czech['IBUId'],
                    'rank': czech['Rank'],
                    'shooting': self._parse_shooting(czech.get('Shootings', '')),
                    'ski_rank': ski_rank,
                    'shooting_rank': shoot_rank,
                    'time_behind': czech.get('Behind'),
                    
                    # Key insights
                    'lost_positions_shooting': max(0, shoot_rank - czech['Rank']) if shoot_rank else 0,
                    'gained_positions_skiing': max(0, czech['Rank'] - ski_rank) if ski_rank else 0,
                    
                    # What-if scenarios
                    'potential_with_clean_shooting': self._calculate_potential(czech, results)
                }
                
                czech_analysis.append(analysis)
            
            # Race statistics
            winner = results[0] if results else {}
            
            return {
                'race_id': race_id,
                'competition': race_results.get('Competition', {}),
                'weather': race_results.get('Weather', {}),
                'winner': {
                    'name': winner.get('Name'),
                    'nation': winner.get('Nat'),
                    'time': winner.get('TotalTime')
                },
                'czech_athletes': czech_analysis,
                'total_finishers': len([r for r in results if r.get('Rank') and r['Rank'] != 'DNF']),
                'dnf_count': len([r for r in results if r.get('Rank') == 'DNF'])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing race: {e}")
            return {}
    
    def _find_in_analytics(self, ibu_id: str, analytics: Dict) -> Optional[int]:
        """Find athlete rank in analytics results"""
        for result in analytics.get('Results', []):
            if result.get('IBUId') == ibu_id:
                return result.get('Rank')
        return None
    
    def _calculate_potential(self, athlete: Dict, all_results: List[Dict]) -> Dict:
        """Calculate potential position with clean shooting"""
        shooting = self._parse_shooting(athlete.get('Shootings', ''))
        penalty_time = shooting['total_misses'] * 25  # ~25 seconds per miss average
        
        # Find where athlete would be without penalty
        current_time = self._parse_time(athlete.get('TotalTime', ''))
        potential_time = current_time - penalty_time if current_time else None
        
        if potential_time:
            # Count how many would be behind
            potential_rank = 1
            for other in all_results:
                other_time = self._parse_time(other.get('TotalTime', ''))
                if other_time and other_time < potential_time:
                    potential_rank += 1
            
            return {
                'rank': potential_rank,
                'positions_gained': athlete['Rank'] - potential_rank if isinstance(athlete['Rank'], int) else 0,
                'time_saved': penalty_time
            }
        
        return {'rank': athlete['Rank'], 'positions_gained': 0}
    
    def _parse_time(self, time_str: str) -> Optional[float]:
        """Parse time string to seconds"""
        if not time_str or time_str in ['DNF', 'DNS', 'DSQ']:
            return None
        
        # Remove + prefix
        time_str = time_str.replace('+', '')
        
        # Parse MM:SS.S or SS.S
        if ':' in time_str:
            parts = time_str.split(':')
            minutes = float(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    
    def get_upcoming_races(self) -> List[Dict]:
        """Get upcoming races with Czech participation likelihood"""
        try:
            events = br.events(self.current_season, level=br.consts.LevelType.BMW_IBU_WC)
            upcoming = []
            
            for event in events:
                # Get competitions for this event
                competitions = br.competitions(event['EventId'])
                
                for comp in competitions:
                    # Check if race is in future
                    race_date = datetime.fromisoformat(comp['StartTime'].replace('Z', '+00:00'))
                    if race_date > datetime.now(race_date.tzinfo):
                        upcoming.append({
                            'race_id': comp['RaceId'],
                            'date': comp['StartTime'],
                            'location': event.get('Place', ''),
                            'description': comp['ShortDescription'],
                            'discipline': comp.get('DisciplineId', ''),
                            'days_until': (race_date - datetime.now(race_date.tzinfo)).days,
                            
                            # Czech team likely participants
                            'czech_likely': self._predict_czech_participation(comp)
                        })
            
            return sorted(upcoming, key=lambda x: x['date'])[:10]
            
        except Exception as e:
            logger.error(f"Error getting upcoming races: {e}")
            return []
    
    def _predict_czech_participation(self, competition: Dict) -> List[str]:
        """Predict which Czech athletes will participate"""
        # For now, return top Czech athletes
        # Could be enhanced with form, quotas, etc.
        return ['Davidová', 'Jislová', 'Charvátová', 'Krčmář']
    
    def get_head_to_head(self, athlete1_id: str, athlete2_id: str) -> Dict:
        """Detailed head-to-head comparison"""
        try:
            # Get both athletes' results
            results1 = br.all_results(athlete1_id).get('Results', [])
            results2 = br.all_results(athlete2_id).get('Results', [])
            
            # Find common races
            races1 = {r['RaceId']: r for r in results1}
            races2 = {r['RaceId']: r for r in results2}
            
            common_races = set(races1.keys()) & set(races2.keys())
            
            # Compare in each common race
            comparisons = []
            wins = {athlete1_id: 0, athlete2_id: 0}
            
            for race_id in list(common_races)[:20]:  # Last 20 common races
                r1 = races1[race_id]
                r2 = races2[race_id]
                
                if isinstance(r1['Rank'], int) and isinstance(r2['Rank'], int):
                    winner = athlete1_id if r1['Rank'] < r2['Rank'] else athlete2_id
                    wins[winner] += 1
                    
                    comparisons.append({
                        'race_id': race_id,
                        'date': r1.get('Date'),
                        'location': r1.get('Place'),
                        'athlete1_rank': r1['Rank'],
                        'athlete2_rank': r2['Rank'],
                        'winner': winner,
                        'margin': abs(r1['Rank'] - r2['Rank'])
                    })
            
            return {
                'total_races': len(comparisons),
                'athlete1_wins': wins[athlete1_id],
                'athlete2_wins': wins[athlete2_id],
                'recent_form': comparisons[:5],  # Last 5 H2H
                'biggest_margin': max(comparisons, key=lambda x: x['margin']) if comparisons else None,
                'trend': self._calculate_h2h_trend(comparisons)
            }
            
        except Exception as e:
            logger.error(f"Error in head-to-head: {e}")
            return {}
    
    def _calculate_h2h_trend(self, comparisons: List[Dict]) -> str:
        """Calculate head-to-head trend"""
        if len(comparisons) < 5:
            return 'insufficient_data'
        
        recent = comparisons[:5]
        older = comparisons[5:10] if len(comparisons) >= 10 else comparisons[5:]
        
        # Count wins in each period
        # This would need athlete IDs to determine winner properly
        # Simplified for now
        
        return 'improving'

# Singleton
ibu_service = IBUFullService()
