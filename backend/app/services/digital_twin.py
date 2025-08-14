"""Core Digital Twin implementation"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import numpy as np
from scipy import signal, stats

from app.models.athlete import Athlete
from app.models.sensor_data import SensorData
from app.schemas.prediction import (
    ShootingPredictionRequest,
    ShootingPredictionResponse,
    ApproachOptimizationRequest,
    ApproachOptimizationResponse,
    FatigueAssessment
)

logger = logging.getLogger(__name__)


class DigitalTwin:
    """Digital Twin for biathlon athlete"""
    
    def __init__(self, athlete: Athlete):
        self.athlete = athlete
        self.current_state = {}
        self.history = []
        
        # Initialize sub-models
        self.lactate_model = LactateEstimator(athlete)
        self.wind_model = WindCompensationModel()
        self.fatigue_model = FatigueModel(athlete)
        
    async def update_state(self, sensor_data: SensorData) -> None:
        """Update current state from sensor data"""
        self.current_state = {
            "timestamp": sensor_data.timestamp,
            "heart_rate": sensor_data.heart_rate,
            "hrv": sensor_data.heart_rate_variability,
            "lactate": sensor_data.lactate_estimated,
            "activity": sensor_data.activity_type,
            "body_sway": {
                "ap": sensor_data.body_sway_ap,
                "ml": sensor_data.body_sway_ml
            },
            "environment": {
                "temperature": sensor_data.temperature,
                "wind_speed": sensor_data.wind_speed,
                "wind_direction": sensor_data.wind_direction
            }
        }
        
        # Update history (keep last 100 states)
        self.history.append(self.current_state)
        if len(self.history) > 100:
            self.history.pop(0)
    
    async def predict_shooting(
        self, 
        request: ShootingPredictionRequest
    ) -> ShootingPredictionResponse:
        """Predict shooting performance"""
        
        # Base accuracy from athlete profile
        if request.position == "prone":
            base_accuracy = self.athlete.prone_accuracy_baseline
        else:
            base_accuracy = self.athlete.standing_accuracy_baseline
        
        # Calculate factors
        hr_factor = self._calculate_hr_factor(request.current_heart_rate)
        lactate_factor = self._calculate_lactate_factor(request.current_lactate)
        fatigue_factor = await self.fatigue_model.get_current_factor()
        stability_factor = self._calculate_stability_factor(request.position)
        
        # Wind effect
        wind_effect = self.wind_model.calculate_effect(
            request.wind_speed,
            request.wind_direction
        )
        
        # Combined prediction
        predicted_accuracy = (
            base_accuracy * 
            hr_factor * 
            lactate_factor * 
            fatigue_factor * 
            stability_factor * 
            (1 + wind_effect["hit_probability_change"])
        )
        
        predicted_accuracy = np.clip(predicted_accuracy, 0, 1)
        
        # Confidence interval (±5%)
        ci_range = 0.05
        confidence_interval = (
            max(0, predicted_accuracy - ci_range),
            min(1, predicted_accuracy + ci_range)
        )
        
        # Contributing factors
        factors = {
            "heart_rate": hr_factor,
            "lactate": lactate_factor,
            "fatigue": fatigue_factor,
            "stability": stability_factor,
            "wind": 1 + wind_effect["hit_probability_change"]
        }
        
        # Generate recommendations
        recommendations = self._generate_shooting_recommendations(
            factors, 
            request
        )
        
        # Critical factors (those below 0.95)
        critical_factors = [
            factor for factor, value in factors.items() 
            if value < 0.95
        ]
        
        return ShootingPredictionResponse(
            timestamp=datetime.utcnow(),
            prediction_type="shooting",
            position=request.position,
            bout_number=request.bout_number,
            predicted_value=predicted_accuracy,
            predicted_accuracy=predicted_accuracy,
            expected_hits=int(predicted_accuracy * 5),
            confidence_score=0.85,  # Model confidence
            confidence_interval=confidence_interval,
            contributing_factors=factors,
            recommendations=recommendations,
            miss_probability=1 - predicted_accuracy,
            critical_factors=critical_factors
        )
    
    async def optimize_approach(
        self,
        request: ApproachOptimizationRequest
    ) -> ApproachOptimizationResponse:
        """Optimize approach to shooting range"""
        
        # Target HR (86% of max)
        target_hr = self.athlete.hr_max * 0.86
        optimal_range = (
            self.athlete.hr_max * 0.83,
            self.athlete.hr_max * 0.87
        )
        
        # HR recovery model (exponential decay)
        current_hr = request.current_heart_rate
        hr_decay_rate = 0.015  # 1.5% per second
        
        # Calculate time to range
        time_to_range = request.distance_to_range / request.current_speed
        
        # Predicted HR at arrival
        predicted_hr = current_hr * np.exp(-hr_decay_rate * time_to_range)
        
        # Generate speed profile
        speed_profile = self._generate_speed_profile(
            request.distance_to_range,
            request.current_speed,
            current_hr,
            target_hr,
            request.terrain
        )
        
        # Determine deceleration point
        if predicted_hr > target_hr + 5:
            decel_point = request.distance_to_range - 150  # Start early
        elif predicted_hr > target_hr:
            decel_point = request.distance_to_range - 100
        else:
            decel_point = request.distance_to_range - 50
        
        # Energy cost calculation
        energy_cost = self._calculate_energy_cost(
            speed_profile,
            request.terrain
        )
        
        # Fatigue impact
        fatigue_impact = await self.fatigue_model.predict_impact(
            energy_cost,
            time_to_range
        )
        
        # Recovery time estimation
        recovery_time = (current_hr - target_hr) / 0.5  # 0.5 bpm/s
        
        # Recommendations
        recommendations = []
        if predicted_hr > optimal_range[1]:
            recommendations.append("SLOW DOWN: Reduce pace by 10-15%")
            recommendations.append("BREATHING: Use 4-7-8 pattern")
        elif predicted_hr < optimal_range[0]:
            recommendations.append("MAINTAIN: Keep current pace")
        
        if request.terrain == "uphill":
            recommendations.append("TECHNIQUE: Shorter strides, higher cadence")
        
        return ApproachOptimizationResponse(
            timestamp=datetime.utcnow(),
            current_hr=current_hr,
            predicted_hr_arrival=predicted_hr,
            target_hr=target_hr,
            optimal_hr_range=optimal_range,
            recommended_speed_profile=speed_profile,
            deceleration_point=decel_point,
            estimated_time_to_range=time_to_range,
            estimated_recovery_time=recovery_time,
            recovery_breathing_pattern="4-7-8",
            energy_cost=energy_cost,
            fatigue_impact=fatigue_impact,
            recommendations=recommendations
        )
    
    def _calculate_hr_factor(self, hr: float) -> float:
        """Calculate HR impact on shooting"""
        hr_pct = hr / self.athlete.hr_max
        
        if 0.80 <= hr_pct <= 0.87:
            return 1.0  # Optimal range
        elif hr_pct < 0.80:
            return 0.97  # Too relaxed
        elif hr_pct > 0.95:
            return 0.85  # Too high
        else:
            # Linear interpolation
            return 1.0 - (hr_pct - 0.87) * 0.15 / 0.08
    
    def _calculate_lactate_factor(self, lactate: Optional[float]) -> float:
        """Calculate lactate impact on shooting"""
        if lactate is None:
            return 1.0
            
        if lactate < 2.0:
            return 1.0
        elif lactate < 4.0:
            return 0.98
        elif lactate < 6.0:
            return 0.95
        else:
            return 0.90
    
    def _calculate_stability_factor(self, position: str) -> float:
        """Calculate stability factor from current state"""
        if not self.current_state:
            return 1.0
            
        sway = self.current_state.get("body_sway", {})
        if not sway:
            return 1.0
            
        # Average sway
        avg_sway = (sway.get("ap", 0) + sway.get("ml", 0)) / 2
        
        # Threshold based on position
        if position == "prone":
            threshold = 0.55  # mm/s
        else:
            threshold = 0.85  # mm/s
            
        if avg_sway < threshold:
            return 1.0
        elif avg_sway < threshold * 1.5:
            return 0.95
        else:
            return 0.90
    
    def _generate_shooting_recommendations(
        self,
        factors: Dict[str, float],
        request: ShootingPredictionRequest
    ) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        # HR recommendations
        if factors["heart_rate"] < 0.95:
            recs.append("BREATHING: Use 4-7-8 technique to lower HR")
            recs.append("TIMING: Wait 5-10s for HR to drop")
        
        # Stability recommendations
        if factors["stability"] < 0.95:
            if request.position == "standing":
                recs.append("STANCE: Widen stance for better stability")
            recs.append("CORE: Engage core muscles")
        
        # Wind recommendations
        if factors["wind"] < 0.95:
            recs.append(f"WIND: Aim {request.wind_speed*0.5:.1f}cm into wind")
            recs.append("TIMING: Wait for wind lull if possible")
        
        # Fatigue recommendations
        if factors["fatigue"] < 0.95:
            recs.append("FOCUS: Extra attention on sight picture")
            recs.append("TRIGGER: Smooth, controlled squeeze")
        
        if not recs:
            recs.append("OPTIMAL: Maintain current approach")
            
        return recs[:3]  # Top 3 recommendations
    
    def _generate_speed_profile(
        self,
        distance: float,
        current_speed: float,
        current_hr: float,
        target_hr: float,
        terrain: str
    ) -> List[Dict[str, float]]:
        """Generate optimal speed profile"""
        profile = []
        
        # Terrain adjustment
        terrain_factor = {
            "uphill": 0.85,
            "flat": 1.0,
            "downhill": 1.15
        }[terrain]
        
        # Generate profile points
        distances = [distance, distance*0.75, distance*0.5, distance*0.25, 0]
        
        for d in distances:
            if d > distance * 0.8:
                # Far from range - maintain speed
                speed = current_speed * terrain_factor
            elif d > distance * 0.3:
                # Middle section - gradual deceleration
                speed = current_speed * terrain_factor * (0.9 + 0.1 * d/distance)
            else:
                # Close to range - controlled approach
                speed = current_speed * terrain_factor * 0.75
                
            profile.append({"distance": d, "speed": round(speed, 1)})
            
        return profile
    
    def _calculate_energy_cost(
        self,
        speed_profile: List[Dict[str, float]],
        terrain: str
    ) -> float:
        """Calculate energy cost of approach"""
        # Simplified energy model (kcal)
        base_cost = sum(s["speed"] * 10 for s in speed_profile)
        
        # Terrain adjustment
        terrain_multiplier = {
            "uphill": 1.5,
            "flat": 1.0,
            "downhill": 0.7
        }[terrain]
        
        return base_cost * terrain_multiplier


class LactateEstimator:
    """HRV-based lactate estimation"""
    
    def __init__(self, athlete: Athlete):
        self.athlete = athlete
        self._calibrate()
    
    def _calibrate(self):
        """Calibrate lactate curve"""
        # Use athlete's individual thresholds if available
        if self.athlete.lactate_threshold_1_hr and self.athlete.lactate_threshold_2_hr:
            self.lt1_hr = self.athlete.lactate_threshold_1_hr
            self.lt2_hr = self.athlete.lactate_threshold_2_hr
        else:
            # Estimate from HR max
            self.lt1_hr = self.athlete.hr_max * 0.75
            self.lt2_hr = self.athlete.hr_max * 0.87
    
    def estimate(
        self,
        heart_rate: float,
        hrv_rmssd: Optional[float] = None,
        duration: float = 0
    ) -> tuple[float, float]:
        """Estimate lactate with confidence"""
        
        # Base estimation from HR zones
        if heart_rate < self.lt1_hr:
            base_lactate = 1.0 + (heart_rate / self.lt1_hr) * 1.0
        elif heart_rate < self.lt2_hr:
            pct = (heart_rate - self.lt1_hr) / (self.lt2_hr - self.lt1_hr)
            base_lactate = 2.0 + pct * 2.0
        else:
            pct = (heart_rate - self.lt2_hr) / (self.athlete.hr_max - self.lt2_hr)
            base_lactate = 4.0 + pct * 8.0
        
        # HRV adjustment
        if hrv_rmssd:
            hrv_factor = (50 - hrv_rmssd) * 0.02
            base_lactate += hrv_factor
        
        # Duration adjustment (lactate accumulation)
        time_factor = duration * 0.0001
        base_lactate += time_factor
        
        # Clip to physiological range
        lactate = np.clip(base_lactate, 0.5, 15.0)
        
        # Confidence based on HR zone
        hr_pct = heart_rate / self.athlete.hr_max
        if 0.70 < hr_pct < 0.90:
            confidence = 0.85
        else:
            confidence = 0.70
            
        return lactate, confidence


class WindCompensationModel:
    """Wind effect on shooting"""
    
    def __init__(self):
        self.bullet_velocity = 320  # m/s for .22LR
        self.target_distance = 50  # meters
        self.target_diameter = 0.045  # 4.5cm
    
    def calculate_effect(
        self,
        wind_speed: float,
        wind_direction: float
    ) -> Dict[str, float]:
        """Calculate wind drift and compensation"""
        
        # Convert to clock position
        clock = (wind_direction / 30) % 12 or 12
        
        # Wind value based on angle
        if clock in [3, 9]:
            wind_value = 1.0  # Full value
        elif clock in [6, 12]:
            wind_value = 0.0  # No value
        else:
            # Calculate based on angle
            angle = min(abs(clock - 3), abs(clock - 9)) * 30
            wind_value = np.sin(np.radians(90 - angle))
        
        # Time of flight
        tof = self.target_distance / self.bullet_velocity
        
        # Drift calculation
        effective_wind = wind_speed * wind_value
        drift_meters = effective_wind * tof * 0.5
        drift_rings = drift_meters / self.target_diameter
        
        # Hit probability change
        if drift_rings < 0.5:
            prob_change = 0
        elif drift_rings < 1.0:
            prob_change = -0.05
        elif drift_rings < 1.5:
            prob_change = -0.15
        else:
            prob_change = -0.30
        
        return {
            "wind_value": wind_value,
            "drift_meters": drift_meters,
            "drift_rings": drift_rings,
            "hit_probability_change": prob_change
        }


class FatigueModel:
    """Fatigue accumulation and recovery model"""
    
    def __init__(self, athlete: Athlete):
        self.athlete = athlete
        self.current_fatigue = 0.3  # Starting fatigue
        self.recovery_rate = 0.01  # Per minute
    
    async def get_current_factor(self) -> float:
        """Get current fatigue factor (1.0 = no fatigue)"""
        return 1.0 - (self.current_fatigue * 0.3)
    
    async def update(self, training_load: float, duration: float):
        """Update fatigue based on training"""
        # Accumulate fatigue
        self.current_fatigue += training_load * 0.001 * duration
        
        # Cap at 1.0
        self.current_fatigue = min(1.0, self.current_fatigue)
    
    async def predict_impact(
        self,
        energy_cost: float,
        time_seconds: float
    ) -> float:
        """Predict fatigue impact"""
        # Simple model: fatigue increases with energy and time
        impact = (energy_cost / 1000) * (time_seconds / 60) * 0.1
        return min(impact, 0.5)
