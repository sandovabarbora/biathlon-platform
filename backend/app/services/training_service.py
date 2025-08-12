"""Training recommendations service"""

from typing import List, Dict
from app.services.ibu_api import ibu_api
from app.api.schemas import TrainingRecommendation, Priority

class TrainingService:
    """Generate training recommendations based on performance"""
    
    def generate_recommendations(self, athlete_id: str) -> List[TrainingRecommendation]:
        """Generate training recommendations for athlete"""
        
        # Get performance data
        performance = ibu_api.get_athlete_performance(athlete_id)
        
        if not performance:
            return []
        
        recommendations = []
        
        # Analyze shooting
        shooting = performance['shooting']
        if shooting['total_accuracy'] < 80:
            priority = Priority.HIGH if shooting['total_accuracy'] < 75 else Priority.MEDIUM
            
            recommendations.append(TrainingRecommendation(
                priority=priority,
                area="Shooting Accuracy",
                description=f"Current {shooting['total_accuracy']:.1f}% is below target 82%",
                expected_impact=f"Each 5% improvement = 2-3 positions gain",
                exercises=[
                    "Dry firing 30 min daily with heart rate zones",
                    "Shooting after high intensity (160+ bpm)",
                    "Breathing control between shots",
                    "Mental training - visualization"
                ],
                metrics_to_track=["Hit rate per training", "Time between shots", "HR at shooting"]
            ))
        
        # Standing vs Prone
        if shooting['standing_accuracy'] < shooting['prone_accuracy'] - 10:
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH,
                area="Standing Shooting",
                description=f"Standing {shooting['standing_accuracy']:.1f}% vs Prone {shooting['prone_accuracy']:.1f}%",
                expected_impact="Closing gap = 2-4 positions per race",
                exercises=[
                    "Core stability - planks progression",
                    "Balance board shooting 20 min",
                    "Wind reading practice",
                    "Standing position holds"
                ],
                metrics_to_track=["Standing group size", "Body sway", "Wind compensation"]
            ))
        
        # Consistency
        if performance['consistency_score'] < 60:
            recommendations.append(TrainingRecommendation(
                priority=Priority.MEDIUM,
                area="Race Consistency",
                description=f"High variation (consistency {performance['consistency_score']:.0f}/100)",
                expected_impact="Stable top 20 finishes",
                exercises=[
                    "Race simulation weekly",
                    "Pre-race routine checklist",
                    "Pressure training scenarios",
                    "Recovery optimization"
                ],
                metrics_to_track=["Rank std deviation", "Pre-race HRV", "Sleep quality"]
            ))
        
        # Recent form
        if performance['recent_form'] < -5:
            recommendations.append(TrainingRecommendation(
                priority=Priority.HIGH,
                area="Form Recovery",
                description=f"Declining trend ({performance['recent_form']:.1f})",
                expected_impact="Return to season average",
                exercises=[
                    "Reduce training load 20%",
                    "Focus on recovery",
                    "Technique video analysis",
                    "Mental reset protocol"
                ],
                metrics_to_track=["Resting HR", "Training stress", "Mood scores"]
            ))
        
        # Ski speed
        ski_stats = performance.get('ski_stats', {})
        if ski_stats.get('ski_speed_percentile') and ski_stats['ski_speed_percentile'] < 50:
            recommendations.append(TrainingRecommendation(
                priority=Priority.MEDIUM,
                area="Ski Speed",
                description=f"Below average ski speed (percentile: {ski_stats['ski_speed_percentile']:.0f})",
                expected_impact="Top 50% = gain 30-60 seconds",
                exercises=[
                    "VO2max intervals 2x/week",
                    "Technique work with video",
                    "Strength - explosive power",
                    "Altitude training camp"
                ],
                metrics_to_track=["Lactate threshold", "Test times", "Power output"]
            ))
        
        return recommendations

# Singleton
training_service = TrainingService()
