"""Analytics service using real IBU data"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from app.services.data_service import data_service
from app.api.schemas import TrainingRecommendation, Priority

class RealAnalyticsService:
    """Analytics using real CSV data"""
    
    def generate_training_recommendations(self, athlete_id: str) -> List[TrainingRecommendation]:
        """Generate recommendations based on real data"""
        
        performance = data_service.get_athlete_performance(athlete_id)
        if not performance:
            return []
        
        recommendations = []
        shooting = performance['shooting']
        
        # Shooting accuracy analysis
        if shooting['total_accuracy'] < 80:
            priority = Priority.HIGH if shooting['total_accuracy'] < 75 else Priority.MEDIUM
            
            recommendations.append(TrainingRecommendation(
                priority=priority,
                area="Shooting Accuracy",
                description=f"Current accuracy {shooting['total_accuracy']:.1f}% is below World Cup average (82%)",
                expected_impact=f"Improving to 80% could gain {int((80 - shooting['total_accuracy']) * 0.8)} positions per race",
                exercises=[
                    "Dry firing 30 min daily with heart rate monitor",
                    "Shooting after high-intensity intervals",
                    "Breathing pattern training (4-7-8 technique)",
                    "Visualization of perfect shooting sequence"
                ],
                metrics_to_track=["Daily hit percentage", "Time between shots", "Heart rate at trigger"]
            ))
        
        # Standing vs Prone difference
        if shooting['standing_accuracy'] < shooting['prone_accuracy'] - 10:
            diff = shooting['prone_accuracy'] - shooting['standing_accuracy']
            
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH,
                area="Standing Shooting Stability",
                description=f"Standing accuracy {diff:.1f}% lower than prone",
                expected_impact="Each 5% improvement typically gains 2-3 positions",
                exercises=[
                    "Core stability work - planks progression",
                    "Balance board shooting practice 20 min",
                    "Standing hold without shooting - 5x2 min",
                    "Wind flag reading exercises"
                ],
                metrics_to_track=["Standing group size", "Sway amplitude", "Time to first shot"]
            ))
        
        # Consistency based on real data
        if performance['consistency_score'] < 60:
            recommendations.append(TrainingRecommendation(
                priority=Priority.MEDIUM,
                area="Performance Consistency",
                description=f"High variability in results (consistency: {performance['consistency_score']:.0f}/100)",
                expected_impact="Consistent top 20 finishes vs current variation",
                exercises=[
                    "Standardized warm-up routine",
                    "Race simulation training weekly",
                    "Mental preparation checklist",
                    "Recovery protocol optimization"
                ],
                metrics_to_track=["Rank standard deviation", "Race-to-race variation", "Pre-race HRV"]
            ))
        
        # Form analysis
        if performance['recent_form'] < -5:
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH,
                area="Form Recovery",
                description=f"Recent form declining (trend: {performance['recent_form']:.1f})",
                expected_impact="Return to season average performance",
                exercises=[
                    "Training load reduction 20%",
                    "Focus on recovery metrics",
                    "Technique video analysis",
                    "Mental reset protocol"
                ],
                metrics_to_track=["Sleep quality", "Resting heart rate", "Training stress balance"]
            ))
        
        # DNF rate
        if performance.get('dnf_rate', 0) > 10:
            recommendations.append(TrainingRecommendation(
                priority=Priority.MEDIUM,
                area="Race Completion",
                description=f"High DNF rate: {performance['dnf_rate']:.1f}%",
                expected_impact="Completing all races adds valuable points and experience",
                exercises=[
                    "Pacing strategy review",
                    "Nutrition plan optimization",
                    "Equipment check protocol",
                    "Mental toughness training"
                ],
                metrics_to_track=["Race completion rate", "Energy levels", "Equipment issues"]
            ))
        
        # Ski performance if available
        if performance.get('ski_stats', {}).get('ski_speed_percentile'):
            if performance['ski_stats']['ski_speed_percentile'] < 50:
                recommendations.append(TrainingRecommendation(
                    priority=Priority.MEDIUM,
                    area="Ski Speed",
                    description=f"Ski speed below average (percentile: {performance['ski_stats']['ski_speed_percentile']:.0f})",
                    expected_impact="Moving to top 50% would gain 30-60 seconds per race",
                    exercises=[
                        "VO2max intervals 2x/week",
                        "Technique work with video",
                        "Strength training focus on power",
                        "Altitude training camp"
                    ],
                    metrics_to_track=["Lactate threshold", "Ski test times", "Power output"]
                ))
        
        return recommendations
    
    def analyze_season_trends(self, athlete_id: str) -> Dict:
        """Analyze season progression using real data"""
        
        if data_service.results_df is None:
            return {}
        
        athlete_results = data_service.results_df[
            data_service.results_df['IBUId'] == athlete_id
        ].copy()
        
        if athlete_results.empty:
            return {}
        
        # Sort by date
        athlete_results = athlete_results.sort_values('StartTime')
        
        # Split season into periods
        total_races = len(athlete_results)
        period_size = max(1, total_races // 4)
        
        periods = {
            'early_season': athlete_results.head(period_size),
            'mid_season_1': athlete_results.iloc[period_size:period_size*2],
            'mid_season_2': athlete_results.iloc[period_size*2:period_size*3],
            'late_season': athlete_results.tail(period_size)
        }
        
        trend_analysis = {}
        
        for period_name, period_data in periods.items():
            ranks = period_data['Rank'].dropna()
            if len(ranks) > 0:
                trend_analysis[period_name] = {
                    'avg_rank': float(ranks.mean()),
                    'best_rank': int(ranks.min()),
                    'races': len(ranks),
                    'shooting_avg': float(period_data['ShootingTotal'].dropna().mean()) if 'ShootingTotal' in period_data else 0
                }
        
        return trend_analysis
    
    def find_similar_athletes(self, athlete_id: str, limit: int = 5) -> List[Dict]:
        """Find athletes with similar performance profile"""
        
        target_perf = data_service.get_athlete_performance(athlete_id)
        if not target_perf:
            return []
        
        all_athletes = data_service.get_athletes(limit=200)
        similarities = []
        
        for athlete in all_athletes:
            if athlete['id'] == athlete_id:
                continue
            
            other_perf = data_service.get_athlete_performance(athlete['id'])
            if not other_perf or other_perf['total_races'] < 5:
                continue
            
            # Calculate similarity score
            rank_diff = abs(target_perf['avg_rank'] - other_perf['avg_rank'])
            shooting_diff = abs(
                target_perf['shooting']['total_accuracy'] - 
                other_perf['shooting']['total_accuracy']
            )
            
            similarity_score = 100 - (rank_diff + shooting_diff / 2)
            
            similarities.append({
                'athlete': athlete,
                'similarity_score': similarity_score,
                'avg_rank': other_perf['avg_rank'],
                'shooting_accuracy': other_perf['shooting']['total_accuracy']
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return similarities[:limit]

# Global instance
real_analytics = RealAnalyticsService()
