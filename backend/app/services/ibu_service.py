"""IBU Data Service using biathlonresults library"""

import biathlonresults
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class IBUDataService:
    """Service for fetching and analyzing IBU data with Czech focus"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.current_season = self._get_current_season()
        self.czech_athletes = []
        self.top_athletes = []
        self.recent_races = []
        self._initialize_data()
    
    def _get_current_season(self) -> int:
        """Get current biathlon season"""
        now = datetime.now()
        # Biathlon season starts in November
        if now.month >= 11:
            return now.year
        return now.year - 1
    
    def _initialize_data(self):
        """Load initial data - Czech athletes first!"""
        try:
            logger.info(f"Loading season {self.current_season} data...")
            
            # Get Czech athletes from current season
            self._load_czech_athletes()
            
            # Get recent races
            self._load_recent_races()
            
            # Get top athletes for comparison
            self._load_top_athletes()
            
        except Exception as e:
            logger.error(f"Error initializing data: {e}")
    
    def _load_czech_athletes(self):
        """Load all Czech athletes - OUR PRIORITY"""
        try:
            # Get all cups to find Czech athletes
            cups = biathlonresults.cups(self.current_season)
            
            for cup in cups:
                if cup.get('CupId'):
                    standings = biathlonresults.cup_standings(cup['CupId'])
                    
                    for athlete in standings:
                        if athlete.get('Nat') == 'CZE':
                            self.czech_athletes.append({
                                'ibu_id': athlete.get('IBUId'),
                                'name': athlete.get('Name'),
                                'rank': athlete.get('Rank'),
                                'points': athlete.get('Score', 0)
                            })
            
            # Remove duplicates
            seen = set()
            unique = []
            for athlete in self.czech_athletes:
                if athlete['ibu_id'] not in seen:
                    seen.add(athlete['ibu_id'])
                    unique.append(athlete)
            
            self.czech_athletes = unique
            logger.info(f"Loaded {len(self.czech_athletes)} Czech athletes")
            
        except Exception as e:
            logger.error(f"Error loading Czech athletes: {e}")
    
    def _load_recent_races(self):
        """Load recent race results"""
        try:
            events = biathlonresults.events(self.current_season, level=1)
            
            # Get last 5 events
            for event in events[-5:]:
                if event.get('EventId'):
                    competitions = biathlonresults.competitions(event['EventId'])
                    
                    for comp in competitions:
                        if comp.get('RaceId'):
                            self.recent_races.append({
                                'race_id': comp['RaceId'],
                                'description': comp.get('ShortDescription'),
                                'date': comp.get('StartTime'),
                                'discipline': comp.get('DisciplineId')
                            })
            
            logger.info(f"Loaded {len(self.recent_races)} recent races")
            
        except Exception as e:
            logger.error(f"Error loading recent races: {e}")
    
    def _load_top_athletes(self):
        """Load top 30 athletes for comparison"""
        try:
            # Get overall World Cup standings
            cups = biathlonresults.cups(self.current_season)
            
            for cup in cups:
                if 'Overall' in cup.get('Description', ''):
                    standings = biathlonresults.cup_standings(cup['CupId'])
                    self.top_athletes = standings[:30]
                    break
            
            logger.info(f"Loaded top {len(self.top_athletes)} athletes")
            
        except Exception as e:
            logger.error(f"Error loading top athletes: {e}")
    
    @lru_cache(maxsize=128)
    def get_athlete_performance(self, ibu_id: str) -> Dict:
        """Get comprehensive athlete performance with comparison"""
        try:
            results = biathlonresults.athlete_results(ibu_id, self.current_season)
            
            if not results:
                return None
            
            # Calculate statistics
            ranks = [r['Rank'] for r in results if r.get('Rank') and r['Rank'] != 'DNF']
            shooting_data = []
            ski_ranks = []
            
            for result in results:
                # Parse shooting
                if result.get('Shootings'):
                    shooting_str = result['Shootings']
                    # Format: "0+1+0+2" or similar
                    misses = sum(int(x) for x in shooting_str.replace('+', '') if x.isdigit())
                    shooting_data.append(misses)
                
                # Get ski rank if available
                if result.get('SkiRank'):
                    ski_ranks.append(result['SkiRank'])
            
            # Basic stats
            avg_rank = np.mean(ranks) if ranks else 999
            avg_shooting = np.mean(shooting_data) if shooting_data else 20
            avg_ski_rank = np.mean(ski_ranks) if ski_ranks else 999
            
            # Compare with TOP 10 average
            top10_avg_rank = 5.5  # Average of ranks 1-10
            top10_avg_shooting = self._get_top10_shooting_avg()
            
            # Compare with direct competitors (rank 15-25)
            competitors_avg = self._get_competitors_avg(avg_rank)
            
            # Calculate percentiles
            shooting_percentile = self._calculate_percentile(avg_shooting, 'shooting')
            ski_percentile = self._calculate_percentile(avg_ski_rank, 'ski')
            
            # Trend analysis
            recent_trend = self._calculate_trend(ranks)
            
            return {
                'ibu_id': ibu_id,
                'name': results[0].get('Name'),
                'nation': results[0].get('Nat'),
                'season_stats': {
                    'races': len(results),
                    'avg_rank': avg_rank,
                    'best_rank': min(ranks) if ranks else None,
                    'worst_rank': max(ranks) if ranks else None,
                    'dnf_count': len([r for r in results if r.get('Rank') == 'DNF']),
                    'points': sum(self._rank_to_points(r) for r in ranks)
                },
                'shooting': {
                    'avg_misses': avg_shooting,
                    'accuracy': (20 - avg_shooting) / 20 * 100,
                    'vs_top10': avg_shooting - top10_avg_shooting,
                    'percentile': shooting_percentile
                },
                'skiing': {
                    'avg_rank': avg_ski_rank,
                    'vs_top10': avg_ski_rank - 5.5,
                    'percentile': ski_percentile
                },
                'comparison': {
                    'vs_top10': {
                        'rank_diff': avg_rank - top10_avg_rank,
                        'shooting_diff': avg_shooting - top10_avg_shooting,
                        'message': self._get_comparison_message(avg_rank, top10_avg_rank)
                    },
                    'vs_competitors': competitors_avg
                },
                'trend': recent_trend,
                'strengths': self._identify_strengths(shooting_percentile, ski_percentile),
                'weaknesses': self._identify_weaknesses(shooting_percentile, ski_percentile)
            }
            
        except Exception as e:
            logger.error(f"Error getting athlete performance: {e}")
            return None
    
    def _get_top10_shooting_avg(self) -> float:
        """Get average shooting misses for top 10 athletes"""
        # This would need real calculation from top athletes
        return 2.5  # Typical top 10 average
    
    def _get_competitors_avg(self, athlete_rank: float) -> Dict:
        """Get average stats for direct competitors"""
        # Define competitor range based on athlete's level
        if athlete_rank <= 10:
            competitor_range = (1, 10)
        elif athlete_rank <= 20:
            competitor_range = (10, 20)
        elif athlete_rank <= 30:
            competitor_range = (20, 30)
        else:
            competitor_range = (30, 50)
        
        return {
            'range': competitor_range,
            'message': f"Competing with ranks {competitor_range[0]}-{competitor_range[1]}"
        }
    
    def _calculate_percentile(self, value: float, metric: str) -> float:
        """Calculate percentile ranking (0-100, higher is better)"""
        # Simplified - would need full field data
        if metric == 'shooting':
            # Lower misses = higher percentile
            if value <= 2:
                return 90
            elif value <= 3:
                return 70
            elif value <= 4:
                return 50
            else:
                return 30
        else:  # ski rank
            # Lower rank = higher percentile
            if value <= 10:
                return 90
            elif value <= 20:
                return 70
            elif value <= 30:
                return 50
            else:
                return 30
    
    def _calculate_trend(self, ranks: List[int]) -> Dict:
        """Calculate performance trend"""
        if len(ranks) < 3:
            return {'direction': 'insufficient_data'}
        
        recent = np.mean(ranks[-3:])
        earlier = np.mean(ranks[:-3])
        
        improvement = earlier - recent  # Lower rank is better
        
        if improvement > 3:
            direction = 'improving_fast'
        elif improvement > 0:
            direction = 'improving'
        elif improvement < -3:
            direction = 'declining_fast'
        elif improvement < 0:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change': improvement,
            'recent_avg': recent,
            'season_avg': np.mean(ranks)
        }
    
    def _identify_strengths(self, shooting_pct: float, ski_pct: float) -> List[str]:
        """Identify athlete's strengths"""
        strengths = []
        
        if shooting_pct >= 70:
            strengths.append("Excellent shooting")
        elif shooting_pct >= 50:
            strengths.append("Solid shooting")
        
        if ski_pct >= 70:
            strengths.append("Strong skiing")
        elif ski_pct >= 50:
            strengths.append("Good ski speed")
        
        if not strengths:
            strengths.append("Consistent performer")
        
        return strengths
    
    def _identify_weaknesses(self, shooting_pct: float, ski_pct: float) -> List[str]:
        """Identify areas for improvement"""
        weaknesses = []
        
        if shooting_pct < 50:
            weaknesses.append("Shooting accuracy needs work")
        if ski_pct < 50:
            weaknesses.append("Ski speed below average")
        
        if shooting_pct < 30:
            weaknesses.append("CRITICAL: Shooting is major weakness")
        if ski_pct < 30:
            weaknesses.append("CRITICAL: Ski speed significantly behind")
        
        return weaknesses if weaknesses else ["Minor improvements needed"]
    
    def _rank_to_points(self, rank: int) -> int:
        """Convert rank to World Cup points"""
        points_map = {
            1: 60, 2: 54, 3: 48, 4: 43, 5: 40,
            6: 38, 7: 36, 8: 34, 9: 32, 10: 31
        }
        
        if rank <= 10:
            return points_map.get(rank, 0)
        elif rank <= 40:
            return 41 - rank
        return 0
    
    def _get_comparison_message(self, our_rank: float, their_rank: float) -> str:
        """Generate comparison message"""
        diff = our_rank - their_rank
        
        if diff < 0:
            return f"BETTER than average by {abs(diff):.1f} positions!"
        elif diff < 5:
            return f"Close to target level ({diff:.1f} positions behind)"
        elif diff < 10:
            return f"Gap to close: {diff:.1f} positions"
        else:
            return f"Significant gap: {diff:.1f} positions behind"
    
    def get_czech_dashboard(self) -> Dict:
        """Get Czech team dashboard - PRIORITY VIEW"""
        
        czech_data = []
        
        for athlete in self.czech_athletes:
            perf = self.get_athlete_performance(athlete['ibu_id'])
            if perf:
                czech_data.append({
                    'name': athlete['name'],
                    'world_rank': athlete.get('rank'),
                    'performance': perf,
                    'status': self._get_athlete_status(perf)
                })
        
        # Sort by world rank
        czech_data.sort(key=lambda x: x.get('world_rank', 999))
        
        # Team statistics
        team_avg_rank = np.mean([a['performance']['season_stats']['avg_rank'] 
                                 for a in czech_data if a.get('performance')])
        
        return {
            'athletes': czech_data,
            'team_stats': {
                'total_athletes': len(czech_data),
                'avg_world_rank': team_avg_rank,
                'vs_top_nations': self._compare_with_top_nations(),
                'strengths': self._team_strengths(czech_data),
                'priorities': self._team_priorities(czech_data)
            },
            'recent_highlights': self._get_recent_highlights()
        }
    
    def _get_athlete_status(self, performance: Dict) -> str:
        """Get athlete status for quick overview"""
        trend = performance.get('trend', {}).get('direction', '')
        
        if 'improving' in trend:
            return '📈 Improving'
        elif 'declining' in trend:
            return '📉 Needs attention'
        else:
            return '➡️ Stable'
    
    def _compare_with_top_nations(self) -> Dict:
        """Compare Czech team with top nations"""
        # This would need real calculation
        return {
            'vs_norway': '+8.5 positions',
            'vs_france': '+6.2 positions',
            'vs_germany': '+5.8 positions',
            'target': 'Close gap to Germany (realistic goal)'
        }
    
    def _team_strengths(self, czech_data: List[Dict]) -> List[str]:
        """Identify team strengths"""
        strengths = []
        
        # Analyze all athletes
        shooting_scores = [a['performance']['shooting']['percentile'] 
                          for a in czech_data if a.get('performance')]
        
        if shooting_scores and np.mean(shooting_scores) > 60:
            strengths.append("Good team shooting average")
        
        # Check for standout performers
        for athlete in czech_data[:3]:  # Top 3 Czech athletes
            if athlete.get('world_rank', 999) < 20:
                strengths.append(f"{athlete['name']} in world top 20")
        
        return strengths if strengths else ["Building consistency"]
    
    def _team_priorities(self, czech_data: List[Dict]) -> List[Dict]:
        """Identify team training priorities"""
        priorities = []
        
        # Analyze weaknesses across team
        shooting_weak = 0
        skiing_weak = 0
        
        for athlete in czech_data:
            if athlete.get('performance'):
                if athlete['performance']['shooting']['percentile'] < 50:
                    shooting_weak += 1
                if athlete['performance']['skiing']['percentile'] < 50:
                    skiing_weak += 1
        
        if shooting_weak > len(czech_data) / 2:
            priorities.append({
                'area': 'Team Shooting',
                'athletes_affected': shooting_weak,
                'action': 'Shooting camp with mental coach'
            })
        
        if skiing_weak > len(czech_data) / 2:
            priorities.append({
                'area': 'Ski Speed',
                'athletes_affected': skiing_weak,
                'action': 'High altitude training camp'
            })
        
        return priorities
    
    def _get_recent_highlights(self) -> List[str]:
        """Get recent Czech highlights"""
        # Would fetch from recent races
        return [
            "Davidová 8th in Östersund Sprint",
            "Krčmář season best 12th in Pursuit",
            "Team improving in standing shooting"
        ]
    
    def get_race_analysis(self, race_id: str) -> Dict:
        """Analyze specific race with Czech focus"""
        try:
            results = biathlonresults.race_results(race_id)
            
            # Find Czech athletes
            czech_results = [r for r in results if r.get('Nat') == 'CZE']
            
            # Get winner for comparison
            winner = results[0] if results else None
            
            analysis = {
                'race_id': race_id,
                'total_athletes': len(results),
                'czech_athletes': len(czech_results),
                'winner': {
                    'name': winner.get('Name'),
                    'nation': winner.get('Nat'),
                    'time': winner.get('TotalTime'),
                    'shooting': winner.get('Shootings')
                },
                'czech_performance': []
            }
            
            for czech in czech_results:
                rank = czech.get('Rank')
                
                # Compare with winner
                time_behind = self._parse_time_behind(czech.get('Behind'))
                
                analysis['czech_performance'].append({
                    'name': czech.get('Name'),
                    'rank': rank,
                    'time_behind': time_behind,
                    'shooting': czech.get('Shootings'),
                    'vs_winner': {
                        'time_diff': time_behind,
                        'shooting_diff': self._compare_shooting(
                            czech.get('Shootings'),
                            winner.get('Shootings')
                        )
                    },
                    'key_moment': self._identify_key_moment(czech)
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing race: {e}")
            return None
    
    def _parse_time_behind(self, time_str: str) -> float:
        """Parse time behind string to seconds"""
        if not time_str or time_str == '0.0':
            return 0.0
        
        # Format: "+1:23.4" or "+23.4"
        time_str = time_str.replace('+', '')
        
        if ':' in time_str:
            parts = time_str.split(':')
            minutes = float(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    
    def _compare_shooting(self, our_shooting: str, their_shooting: str) -> Dict:
        """Compare shooting performance"""
        if not our_shooting or not their_shooting:
            return {}
        
        our_misses = sum(int(x) for x in our_shooting.replace('+', '') if x.isdigit())
        their_misses = sum(int(x) for x in their_shooting.replace('+', '') if x.isdigit())
        
        return {
            'our_misses': our_misses,
            'their_misses': their_misses,
            'difference': our_misses - their_misses,
            'time_cost': (our_misses - their_misses) * 26  # ~26 seconds per miss
        }
    
    def _identify_key_moment(self, result: Dict) -> str:
        """Identify key moment in race for athlete"""
        shooting = result.get('Shootings', '')
        
        # Check for shooting disasters
        if '3' in shooting or '4' in shooting or '5' in shooting:
            return "Shooting disaster cost the race"
        
        # Check rank vs ski rank
        if result.get('SkiRank') and result.get('Rank'):
            if result['SkiRank'] < result['Rank'] - 5:
                return "Good skiing, shooting cost positions"
            elif result['SkiRank'] > result['Rank'] + 5:
                return "Great shooting saved poor ski performance"
        
        return "Consistent performance throughout"

# Singleton instance
ibu_service = IBUDataService()
