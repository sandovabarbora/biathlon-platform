"""IBU API Service using biathlonresults library"""

import biathlonresults as br
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class IBUApiService:
    """Service for fetching real-time IBU data"""
    
    def __init__(self):
        self.current_season = self._get_current_season()
        logger.info(f"Initialized IBU API for season {self.current_season}")
    
    def _get_current_season(self) -> int:
        """Get current biathlon season"""
        now = datetime.now()
        return now.year if now.month >= 11 else now.year - 1
    
    def get_athletes(self, nation: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get athletes from IBU API"""
        try:
            athletes = []
            
            # Get overall World Cup standings for current season
            cups = br.get_cups(self.current_season)
            
            # Find overall cup
            overall_cup = None
            for cup in cups:
                if 'Overall' in cup.get('Description', ''):
                    overall_cup = cup
                    break
            
            if not overall_cup:
                logger.warning("No overall cup found")
                return []
            
            # Get standings
            standings = br.get_cup_standings(overall_cup['CupId'])
            
            # Process athletes
            for standing in standings[:limit]:
                if nation and standing.get('Nat') != nation.upper():
                    continue
                
                athlete = {
                    'id': standing.get('IBUId'),
                    'name': standing.get('Name'),
                    'nation': standing.get('Nat'),
                    'world_cup_rank': standing.get('Rank'),
                    'world_cup_points': standing.get('Score', 0),
                    'active': True
                }
                athletes.append(athlete)
            
            # If filtering by nation, might need more data
            if nation:
                return [a for a in athletes if a['nation'] == nation.upper()][:limit]
            
            return athletes[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching athletes: {e}")
            return []
    
    def get_athlete_performance(self, athlete_id: str) -> Optional[Dict]:
        """Get athlete performance from IBU API"""
        try:
            # Get athlete results for current season
            results = br.get_athlete_results(athlete_id, self.current_season)
            
            if not results:
                logger.warning(f"No results found for athlete {athlete_id}")
                return None
            
            # Calculate statistics
            ranks = []
            shooting_misses = []
            ski_ranks = []
            
            for result in results:
                # Get rank (skip DNF, DNS, etc.)
                rank = result.get('Rank')
                if rank and isinstance(rank, (int, float)):
                    ranks.append(int(rank))
                
                # Get shooting (format varies: "0+1+0+2" or "0 1 0 2")
                shooting = result.get('Shootings', '')
                if shooting:
                    # Count total misses
                    misses = sum(int(x) for x in shooting if x.isdigit())
                    shooting_misses.append(misses)
                
                # Get ski rank if available
                ski_rank = result.get('SkiRank')
                if ski_rank and isinstance(ski_rank, (int, float)):
                    ski_ranks.append(int(ski_rank))
            
            # Calculate averages
            avg_rank = sum(ranks) / len(ranks) if ranks else 999
            avg_misses = sum(shooting_misses) / len(shooting_misses) if shooting_misses else 20
            avg_ski_rank = sum(ski_ranks) / len(ski_ranks) if ski_ranks else 999
            
            # Calculate shooting accuracy (20 shots per race standard)
            shooting_accuracy = ((20 - avg_misses) / 20 * 100) if avg_misses < 20 else 0
            
            # Recent form (last 5 races vs season average)
            recent_form = 0
            if len(ranks) >= 5:
                recent_avg = sum(ranks[-5:]) / 5
                recent_form = (avg_rank - recent_avg) * 2  # Positive if improving
            
            # Calculate consistency
            if len(ranks) > 1:
                variance = sum((r - avg_rank) ** 2 for r in ranks) / len(ranks)
                std_dev = variance ** 0.5
                consistency = max(0, 100 - std_dev * 2)
            else:
                consistency = 50
            
            # Get athlete info from first result
            first_result = results[0]
            
            return {
                'athlete_id': athlete_id,
                'name': first_result.get('Name', ''),
                'nation': first_result.get('Nat', ''),
                'total_races': len(results),
                'races_finished': len(ranks),
                'avg_rank': float(avg_rank),
                'median_rank': float(sorted(ranks)[len(ranks)//2]) if ranks else 0,
                'best_rank': min(ranks) if ranks else 0,
                'worst_rank': max(ranks) if ranks else 0,
                'shooting': {
                    'total_accuracy': float(shooting_accuracy),
                    'prone_accuracy': float(shooting_accuracy + 5),  # Typically better
                    'standing_accuracy': float(shooting_accuracy - 5),  # Typically worse
                    'avg_misses_per_race': float(avg_misses)
                },
                'avg_ski_time': 0,  # Not directly available from API
                'consistency_score': float(consistency),
                'recent_form': float(recent_form),
                'points_total': self._calculate_points(ranks),
                'ski_stats': {
                    'avg_ski_rank': float(avg_ski_rank) if ski_ranks else None,
                    'ski_speed_percentile': max(0, 100 - avg_ski_rank) if ski_ranks else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching athlete performance: {e}")
            return None
    
    def _calculate_points(self, ranks: List[int]) -> int:
        """Calculate World Cup points from ranks"""
        points_map = {
            1: 60, 2: 54, 3: 48, 4: 43, 5: 40,
            6: 38, 7: 36, 8: 34, 9: 32, 10: 31,
            11: 30, 12: 29, 13: 28, 14: 27, 15: 26,
            16: 25, 17: 24, 18: 23, 19: 22, 20: 21,
            21: 20, 22: 19, 23: 18, 24: 17, 25: 16,
            26: 15, 27: 14, 28: 13, 29: 12, 30: 11,
            31: 10, 32: 9, 33: 8, 34: 7, 35: 6,
            36: 5, 37: 4, 38: 3, 39: 2, 40: 1
        }
        
        total = 0
        for rank in ranks:
            if rank <= 40:
                total += points_map.get(rank, 0)
        return total
    
    def get_recent_races(self, limit: int = 10) -> List[Dict]:
        """Get recent races from API"""
        try:
            events = br.get_events(self.current_season, level=1)
            races = []
            
            for event in events[-3:]:  # Last 3 events
                if event.get('EventId'):
                    competitions = br.get_competitions(event['EventId'])
                    
                    for comp in competitions:
                        races.append({
                            'race_id': comp.get('RaceId'),
                            'date': comp.get('StartTime'),
                            'location': event.get('Place', ''),
                            'description': comp.get('ShortDescription', ''),
                            'discipline': comp.get('DisciplineId', '')
                        })
            
            return races[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching races: {e}")
            return []

# Singleton
ibu_api = IBUApiService()
