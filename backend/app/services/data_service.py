"""Service for loading and processing real IBU data from CSV files"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class DataService:
    """Service for handling real biathlon data from CSV files"""
    
    def __init__(self):
        self.data_path = Path("../data")
        self.results_df = None
        self.course_time_df = None
        self.range_time_df = None
        self.shooting_time_df = None
        self.standings_df = None
        self._load_all_data()
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        return obj
    
    def _load_all_data(self):
        """Load all CSV files into memory"""
        try:
            logger.info("Loading real IBU data from CSV files...")
            
            # Load main results
            results_path = self.data_path / "results.csv"
            if results_path.exists():
                self.results_df = pd.read_csv(results_path)
                logger.info(f"Loaded results.csv: {len(self.results_df)} rows")
                
                # Clean and prepare data
                self.results_df['Rank'] = pd.to_numeric(self.results_df['Rank'], errors='coerce')
                self.results_df['ShootingTotal'] = pd.to_numeric(self.results_df['ShootingTotal'], errors='coerce')
                self.results_df['StartTime'] = pd.to_datetime(self.results_df['StartTime'], errors='coerce')
            
            # Load course time analytics
            course_path = self.data_path / "analytics_course_time.csv"
            if course_path.exists():
                self.course_time_df = pd.read_csv(course_path)
                logger.info(f"Loaded course time: {len(self.course_time_df)} rows")
            
            # Load range time analytics
            range_path = self.data_path / "analytics_range_time.csv"
            if range_path.exists():
                self.range_time_df = pd.read_csv(range_path)
                logger.info(f"Loaded range time: {len(self.range_time_df)} rows")
            
            # Load shooting time analytics
            shooting_path = self.data_path / "analytics_shooting_time.csv"
            if shooting_path.exists():
                self.shooting_time_df = pd.read_csv(shooting_path)
                logger.info(f"Loaded shooting time: {len(self.shooting_time_df)} rows")
            
            # Load World Cup standings
            standings_path = self.data_path / "world_cup_standings.csv"
            if standings_path.exists():
                self.standings_df = pd.read_csv(standings_path)
                logger.info(f"Loaded standings: {len(self.standings_df)} rows")
                
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    @lru_cache(maxsize=128)
    def get_athletes(self, nation: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get list of unique athletes"""
        if self.results_df is None:
            return []
        
        # Get unique athletes
        athletes_df = self.results_df[['IBUId', 'Name', 'Nat']].drop_duplicates()
        
        # Filter by nation if specified
        if nation:
            athletes_df = athletes_df[athletes_df['Nat'] == nation.upper()]
        
        # Add statistics
        athletes = []
        for _, row in athletes_df.head(limit).iterrows():
            athlete_results = self.results_df[self.results_df['IBUId'] == row['IBUId']]
            
            # Calculate basic stats with proper type conversion
            ranks = athlete_results['Rank'].dropna()
            
            athlete_data = {
                'id': str(row['IBUId']),  # Convert to string
                'name': str(row['Name']),
                'nation': str(row['Nat']),
                'total_races': int(len(athlete_results)),
                'avg_rank': float(ranks.mean()) if len(ranks) > 0 else None,
                'best_rank': int(ranks.min()) if len(ranks) > 0 else None,
                'active': True
            }
            
            # Add World Cup points if available
            if self.standings_df is not None:
                standings = self.standings_df[self.standings_df['IBUId'] == row['IBUId']]
                if not standings.empty:
                    athlete_data['world_cup_points'] = int(standings['Score'].sum())
                    athlete_data['world_cup_rank'] = int(standings['Rank'].min())
            
            athletes.append(athlete_data)
        
        # Sort by average rank
        athletes.sort(key=lambda x: x.get('avg_rank', 999))
        
        return athletes
    
    def get_athlete_performance(self, athlete_id: str) -> Optional[Dict]:
        """Get detailed performance statistics for an athlete"""
        if self.results_df is None:
            return None
        
        # Get athlete's results
        athlete_results = self.results_df[self.results_df['IBUId'] == athlete_id]
        
        if athlete_results.empty:
            return None
        
        # Calculate statistics with type conversion
        ranks = athlete_results['Rank'].dropna()
        shooting_totals = athlete_results['ShootingTotal'].dropna()
        
        # Parse shooting details
        shooting_stats = self._calculate_shooting_stats(athlete_results)
        
        # Get ski performance from course time
        ski_stats = self._calculate_ski_stats(athlete_id)
        
        # Calculate consistency
        consistency = 100 - min(ranks.std() * 2, 100) if len(ranks) > 1 else 50
        
        # Calculate recent form (last 5 vs all)
        recent_form = 0
        if len(ranks) >= 5:
            recent_avg = ranks.tail(5).mean()
            overall_avg = ranks.mean()
            recent_form = (overall_avg - recent_avg) * 2
        
        # Calculate World Cup points
        points = self._calculate_total_points(ranks)
        
        # Convert all numpy types to Python native types
        return self._convert_numpy_types({
            'athlete_id': str(athlete_id),
            'name': str(athlete_results.iloc[0]['Name']),
            'nation': str(athlete_results.iloc[0]['Nat']),
            'total_races': int(len(athlete_results)),
            'races_finished': int(len(ranks)),
            'avg_rank': float(ranks.mean()) if len(ranks) > 0 else 0,
            'median_rank': float(ranks.median()) if len(ranks) > 0 else 0,
            'best_rank': int(ranks.min()) if len(ranks) > 0 else 0,
            'worst_rank': int(ranks.max()) if len(ranks) > 0 else 0,
            'shooting': shooting_stats,
            'ski_stats': ski_stats,
            'consistency_score': float(consistency),
            'recent_form': float(recent_form),
            'points_total': int(points),
            'dnf_rate': float((len(athlete_results) - len(ranks)) / len(athlete_results) * 100) if len(athlete_results) > 0 else 0
        })
    
    def _calculate_shooting_stats(self, results_df: pd.DataFrame) -> Dict:
        """Calculate detailed shooting statistics"""
        
        shooting_data = results_df['Shootings'].dropna()
        total_misses = results_df['ShootingTotal'].dropna()
        
        prone_hits = []
        standing_hits = []
        
        for shooting_str in shooting_data:
            # Parse shooting string format: "0+1 0+0 1+0 0+2"
            parts = str(shooting_str).split()
            
            for i, part in enumerate(parts):
                if '+' in part:
                    try:
                        misses = int(part.split('+')[0])
                        hits = 5 - misses
                        
                        if i < len(parts) / 2:
                            prone_hits.append(hits)
                        else:
                            standing_hits.append(hits)
                    except:
                        continue
        
        # Calculate accuracies
        prone_accuracy = (sum(prone_hits) / (len(prone_hits) * 5) * 100) if prone_hits else 0
        standing_accuracy = (sum(standing_hits) / (len(standing_hits) * 5) * 100) if standing_hits else 0
        
        # Total accuracy from ShootingTotal column
        total_shots = len(total_misses) * 20
        total_hits = total_shots - total_misses.sum()
        total_accuracy = (total_hits / total_shots * 100) if total_shots > 0 else 0
        
        # Shooting time analysis if available
        avg_shooting_time = None
        if self.shooting_time_df is not None:
            athlete_shooting = self.shooting_time_df[
                self.shooting_time_df['IBUId'] == results_df.iloc[0]['IBUId']
            ]
            if not athlete_shooting.empty:
                shooting_times = athlete_shooting['TotalTime'].dropna()
                avg_shooting_time = self._parse_time_average(shooting_times)
        
        return {
            'total_accuracy': float(total_accuracy),
            'prone_accuracy': float(prone_accuracy),
            'standing_accuracy': float(standing_accuracy),
            'avg_shooting_time': avg_shooting_time,
            'avg_misses_per_race': float(total_misses.mean()) if len(total_misses) > 0 else 0
        }
    
    def _calculate_ski_stats(self, athlete_id: str) -> Dict:
        """Calculate skiing performance statistics"""
        
        ski_stats = {
            'avg_course_time': None,
            'avg_range_time': None,
            'ski_speed_percentile': None
        }
        
        # Course time analysis
        if self.course_time_df is not None:
            athlete_course = self.course_time_df[self.course_time_df['IBUId'] == athlete_id]
            if not athlete_course.empty:
                course_ranks = athlete_course['Rank'].dropna()
                if len(course_ranks) > 0:
                    ski_stats['avg_course_rank'] = float(course_ranks.mean())
                    ski_stats['ski_speed_percentile'] = float(max(0, 100 - ski_stats['avg_course_rank']))
        
        # Range time analysis
        if self.range_time_df is not None:
            athlete_range = self.range_time_df[self.range_time_df['IBUId'] == athlete_id]
            if not athlete_range.empty:
                range_ranks = athlete_range['Rank'].dropna()
                if len(range_ranks) > 0:
                    ski_stats['avg_range_rank'] = float(range_ranks.mean())
        
        return ski_stats
    
    def _calculate_total_points(self, ranks: pd.Series) -> int:
        """Calculate total World Cup points based on rankings"""
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
        
        total_points = 0
        for rank in ranks:
            if not pd.isna(rank) and rank <= 40:
                total_points += points_map.get(int(rank), 0)
        
        return total_points
    
    def _parse_time_average(self, time_series: pd.Series) -> Optional[float]:
        """Parse time strings and calculate average"""
        return None
    
    def get_races(self) -> List[Dict]:
        """Get list of unique races"""
        if self.results_df is None:
            return []
        
        # Get unique races
        races = self.results_df.groupby('RaceId').agg({
            'StartTime': 'first',
            'Name': 'count'
        }).reset_index()
        
        races.columns = ['race_id', 'date', 'total_athletes']
        races = races.sort_values('date', ascending=False)
        
        # Convert to native types
        result = []
        for _, row in races.head(50).iterrows():
            result.append({
                'race_id': str(row['race_id']),
                'date': str(row['date']) if pd.notna(row['date']) else None,
                'total_athletes': int(row['total_athletes'])
            })
        
        return result
    
    def get_head_to_head(self, athlete1_id: str, athlete2_id: str) -> Dict:
        """Compare two athletes head-to-head"""
        if self.results_df is None:
            return {}
        
        # Find common races
        races1 = set(self.results_df[self.results_df['IBUId'] == athlete1_id]['RaceId'])
        races2 = set(self.results_df[self.results_df['IBUId'] == athlete2_id]['RaceId'])
        common_races = races1.intersection(races2)
        
        wins = {athlete1_id: 0, athlete2_id: 0}
        
        for race_id in common_races:
            result1 = self.results_df[
                (self.results_df['IBUId'] == athlete1_id) & 
                (self.results_df['RaceId'] == race_id)
            ]['Rank'].values
            
            result2 = self.results_df[
                (self.results_df['IBUId'] == athlete2_id) & 
                (self.results_df['RaceId'] == race_id)
            ]['Rank'].values
            
            if len(result1) > 0 and len(result2) > 0:
                rank1 = result1[0]
                rank2 = result2[0]
                
                if not pd.isna(rank1) and not pd.isna(rank2):
                    if rank1 < rank2:
                        wins[athlete1_id] += 1
                    else:
                        wins[athlete2_id] += 1
        
        return {
            'total_races': len(common_races),
            'athlete1_wins': int(wins[athlete1_id]),
            'athlete2_wins': int(wins[athlete2_id])
        }

# Global instance
data_service = DataService()
