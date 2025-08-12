"""Analytics service for performance calculations"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import numpy as np
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.athlete import Athlete, RaceResult, Race
from app.api.schemas import (
    PerformanceStats,
    ShootingStats,
    TrainingRecommendation,
    Priority,
    ComparisonResult
)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_performance_stats(
        self, 
        athlete_id: int,
        season: Optional[int] = None
    ) -> Optional[PerformanceStats]:
        """Calculate comprehensive performance statistics"""
        
        query = self.db.query(RaceResult).filter(
            RaceResult.athlete_id == athlete_id
        )
        
        # Filter by season if specified
        if season:
            start_date = datetime(season, 11, 1)
            end_date = datetime(season + 1, 3, 31)
            query = query.join(Race).filter(
                Race.date >= start_date,
                Race.date <= end_date
            )
        
        results = query.all()
        
        if not results:
            return None
        
        # Calculate rank statistics
        ranks = [r.rank for r in results if r.rank]
        
        # Calculate shooting statistics
        shooting_stats = self._calculate_shooting_stats(results)
        
        # Calculate consistency (lower std = higher score)
        consistency = 100 - min(np.std(ranks) * 2, 100) if len(ranks) > 1 else 50
        
        # Calculate recent form
        recent_form = self._calculate_recent_form(results)
        
        # Calculate World Cup points (top 40 get points)
        points = sum(self._calculate_points(r.rank) for r in results if r.rank)
        
        return PerformanceStats(
            athlete_id=athlete_id,
            total_races=len(results),
            avg_rank=np.mean(ranks) if ranks else 0,
            median_rank=np.median(ranks) if ranks else 0,
            best_rank=min(ranks) if ranks else 0,
            worst_rank=max(ranks) if ranks else 0,
            shooting=shooting_stats,
            avg_ski_time=np.mean([r.ski_time for r in results if r.ski_time]),
            consistency_score=consistency,
            recent_form=recent_form,
            points_total=points
        )
    
    def _calculate_shooting_stats(self, results: List[RaceResult]) -> ShootingStats:
        """Calculate shooting statistics"""
        total_shots = len(results) * 20  # 4 rounds * 5 shots
        total_misses = sum(r.shooting_total for r in results if r.shooting_total)
        
        # Parse prone and standing separately
        prone_misses = 0
        standing_misses = 0
        prone_rounds = 0
        standing_rounds = 0
        
        for r in results:
            if r.shooting_prone:
                # Format: "0+1" means 0 misses in first, 1 in second
                parts = r.shooting_prone.split('+')
                for p in parts:
                    if p.isdigit():
                        prone_misses += int(p)
                        prone_rounds += 1
            
            if r.shooting_standing:
                parts = r.shooting_standing.split('+')
                for p in parts:
                    if p.isdigit():
                        standing_misses += int(p)
                        standing_rounds += 1
        
        total_accuracy = ((total_shots - total_misses) / total_shots * 100) if total_shots > 0 else 0
        prone_accuracy = ((prone_rounds * 5 - prone_misses) / (prone_rounds * 5) * 100) if prone_rounds > 0 else 0
        standing_accuracy = ((standing_rounds * 5 - standing_misses) / (standing_rounds * 5) * 100) if standing_rounds > 0 else 0
        
        return ShootingStats(
            total_accuracy=total_accuracy,
            prone_accuracy=prone_accuracy,
            standing_accuracy=standing_accuracy
        )
    
    def _calculate_recent_form(self, results: List[RaceResult]) -> float:
        """Calculate recent form trend"""
        if len(results) < 5:
            return 0.0
        
        # Sort by race date
        sorted_results = sorted(results, key=lambda x: x.race.date if x.race else datetime.now())
        
        # Compare last 5 races to overall average
        recent_ranks = [r.rank for r in sorted_results[-5:] if r.rank]
        all_ranks = [r.rank for r in sorted_results if r.rank]
        
        if not recent_ranks or not all_ranks:
            return 0.0
        
        recent_avg = np.mean(recent_ranks)
        overall_avg = np.mean(all_ranks)
        
        # Positive = improving (lower rank is better)
        return (overall_avg - recent_avg) * 2
    
    def _calculate_points(self, rank: int) -> int:
        """Calculate World Cup points based on rank"""
        if rank <= 0 or rank > 40:
            return 0
        
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
        
        return points_map.get(rank, 0)
    
    def generate_training_recommendations(self, athlete_id: int) -> List[TrainingRecommendation]:
        """Generate personalized training recommendations"""
        
        stats = self.calculate_performance_stats(athlete_id)
        if not stats:
            return []
        
        recommendations = []
        
        # Shooting accuracy check
        if stats.shooting.total_accuracy < 80:
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH if stats.shooting.total_accuracy < 75 else Priority.MEDIUM,
                area="Shooting Accuracy",
                description=f"Current accuracy at {stats.shooting.total_accuracy:.1f}% is below target",
                expected_impact="Each 5% improvement typically gains 3-5 positions",
                exercises=[
                    "Dry firing practice - 30 minutes daily",
                    "Breathing control exercises between shots",
                    "Heart rate management training",
                    "Visualization of perfect shooting sequence"
                ],
                metrics_to_track=["Daily hit rate", "Time per shot", "Heart rate at trigger"]
            ))
        
        # Standing vs Prone
        if stats.shooting.standing_accuracy < stats.shooting.prone_accuracy - 10:
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH,
                area="Standing Shooting",
                description=f"Standing accuracy {stats.shooting.standing_accuracy:.1f}% vs prone {stats.shooting.prone_accuracy:.1f}%",
                expected_impact="Closing this gap could improve average rank by 2-4 positions",
                exercises=[
                    "Core stability exercises - planks and side planks",
                    "Balance board shooting practice",
                    "Wind reading and adjustment drills",
                    "Standing position hold practice (no shooting)"
                ],
                metrics_to_track=["Standing hit rate", "Body sway measurement", "Wind compensation accuracy"]
            ))
        
        # Consistency
        if stats.consistency_score < 60:
            recommendations.append(TrainingRecommendation(
                priority=Priority.MEDIUM,
                area="Race Consistency",
                description=f"Consistency score {stats.consistency_score:.1f} indicates high variability",
                expected_impact="More predictable performance and better season ranking",
                exercises=[
                    "Develop pre-race routine checklist",
                    "Mental imagery training",
                    "Pressure simulation in training",
                    "Race pace management practice"
                ],
                metrics_to_track=["Rank standard deviation", "Split time consistency", "Mental state scores"]
            ))
        
        # Recent form
        if stats.recent_form < -5:
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH,
                area="Form Recovery",
                description="Recent performances showing decline",
                expected_impact="Return to season average performance",
                exercises=[
                    "Recovery protocol review",
                    "Training load adjustment",
                    "Technique video analysis",
                    "Mental reset exercises"
                ],
                metrics_to_track=["Training load", "Recovery metrics", "Technical checkpoints"]
            ))
        
        return recommendations
    
    def compare_athletes(self, athlete1_id: int, athlete2_id: int) -> ComparisonResult:
        """Compare two athletes head-to-head"""
        
        athlete1 = self.db.query(Athlete).filter(Athlete.id == athlete1_id).first()
        athlete2 = self.db.query(Athlete).filter(Athlete.id == athlete2_id).first()
        
        if not athlete1 or not athlete2:
            raise ValueError("One or both athletes not found")
        
        stats1 = self.calculate_performance_stats(athlete1_id)
        stats2 = self.calculate_performance_stats(athlete2_id)
        
        if not stats1 or not stats2:
            raise ValueError("Insufficient data for comparison")
        
        # Head-to-head record
        h2h_wins = self._calculate_head_to_head(athlete1_id, athlete2_id)
        
        return ComparisonResult(
            athlete1=athlete1,
            athlete2=athlete2,
            better_shooting=athlete1.name if stats1.shooting.total_accuracy > stats2.shooting.total_accuracy else athlete2.name,
            better_skiing=athlete1.name if stats1.avg_ski_time < stats2.avg_ski_time else athlete2.name,
            better_consistency=athlete1.name if stats1.consistency_score > stats2.consistency_score else athlete2.name,
            head_to_head_wins=h2h_wins
        )
    
    def _calculate_head_to_head(self, athlete1_id: int, athlete2_id: int) -> dict:
        """Calculate head-to-head record"""
        
        # Find races where both competed
        races_athlete1 = self.db.query(RaceResult.race_id).filter(
            RaceResult.athlete_id == athlete1_id
        ).subquery()
        
        races_athlete2 = self.db.query(RaceResult.race_id).filter(
            RaceResult.athlete_id == athlete2_id
        ).subquery()
        
        common_races = self.db.query(RaceResult.race_id).filter(
            RaceResult.race_id.in_(races_athlete1),
            RaceResult.race_id.in_(races_athlete2)
        ).distinct().all()
        
        wins = {athlete1_id: 0, athlete2_id: 0}
        
        for race_id in common_races:
            result1 = self.db.query(RaceResult).filter(
                RaceResult.race_id == race_id[0],
                RaceResult.athlete_id == athlete1_id
            ).first()
            
            result2 = self.db.query(RaceResult).filter(
                RaceResult.race_id == race_id[0],
                RaceResult.athlete_id == athlete2_id
            ).first()
            
            if result1 and result2 and result1.rank and result2.rank:
                if result1.rank < result2.rank:
                    wins[athlete1_id] += 1
                else:
                    wins[athlete2_id] += 1
        
        return {"athlete1_wins": wins[athlete1_id], "athlete2_wins": wins[athlete2_id]}
    
    def analyze_trends(self, athlete_id: int, period: str) -> dict:
        """Analyze performance trends over specified period"""
        
        query = self.db.query(RaceResult).filter(
            RaceResult.athlete_id == athlete_id
        ).join(Race).order_by(Race.date)
        
        # Filter by period
        if period == "last5":
            results = query.limit(5).all()
        elif period == "last10":
            results = query.limit(10).all()
        elif period == "season":
            current_year = datetime.now().year
            season_start = datetime(current_year - 1, 11, 1) if datetime.now().month < 11 else datetime(current_year, 11, 1)
            results = query.filter(Race.date >= season_start).all()
        else:
            results = query.all()
        
        if not results:
            return None
        
        ranks = [r.rank for r in results if r.rank]
        shooting_totals = [r.shooting_total for r in results if r.shooting_total is not None]
        
        # Calculate trend using linear regression
        if len(ranks) > 1:
            x = np.arange(len(ranks))
            z = np.polyfit(x, ranks, 1)
            trend_direction = "improving" if z[0] < 0 else "declining" if z[0] > 0 else "stable"
        else:
            trend_direction = "insufficient_data"
        
        return {
            "period": period,
            "races_analyzed": len(results),
            "trend_direction": trend_direction,
            "avg_rank": np.mean(ranks) if ranks else 0,
            "rank_std": np.std(ranks) if len(ranks) > 1 else 0,
            "avg_shooting_misses": np.mean(shooting_totals) if shooting_totals else 0,
            "best_rank": min(ranks) if ranks else 0,
            "worst_rank": max(ranks) if ranks else 0
        }
