"""Feature engineering for ML models"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy import signal
from scipy.stats import skew, kurtosis


class FeatureEngineer:
    """Feature engineering for biathlon data"""
    
    @staticmethod
    def extract_hrv_features(rr_intervals: List[float]) -> Dict[str, float]:
        """Extract HRV features from RR intervals"""
        if len(rr_intervals) < 2:
            return {}
        
        rr = np.array(rr_intervals)
        
        # Time domain features
        rmssd = np.sqrt(np.mean(np.diff(rr) ** 2))
        sdnn = np.std(rr)
        pnn50 = np.sum(np.abs(np.diff(rr)) > 50) / len(rr) * 100
        
        # Frequency domain features (simplified)
        # Would need proper spectral analysis in production
        
        return {
            "rMSSD": float(rmssd),
            "SDNN": float(sdnn),
            "pNN50": float(pnn50),
        }
    
    @staticmethod
    def extract_imu_features(
        acceleration: np.ndarray,
        angular_velocity: np.ndarray,
        sampling_rate: int = 200
    ) -> Dict[str, float]:
        """Extract biomechanical features from IMU data"""
        
        # Magnitude
        acc_magnitude = np.linalg.norm(acceleration, axis=1)
        gyro_magnitude = np.linalg.norm(angular_velocity, axis=1)
        
        # Statistical features
        features = {
            "acc_mean": float(np.mean(acc_magnitude)),
            "acc_std": float(np.std(acc_magnitude)),
            "acc_max": float(np.max(acc_magnitude)),
            "acc_min": float(np.min(acc_magnitude)),
            "acc_skew": float(skew(acc_magnitude)),
            "acc_kurtosis": float(kurtosis(acc_magnitude)),
            
            "gyro_mean": float(np.mean(gyro_magnitude)),
            "gyro_std": float(np.std(gyro_magnitude)),
            "gyro_max": float(np.max(gyro_magnitude)),
        }
        
        # Frequency domain features
        freqs, psd = signal.welch(acc_magnitude, sampling_rate, nperseg=min(256, len(acc_magnitude)))
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(psd)
        features["dominant_freq"] = float(freqs[dominant_freq_idx])
        
        # Energy in different bands
        low_band = psd[(freqs >= 0) & (freqs < 5)].sum()
        mid_band = psd[(freqs >= 5) & (freqs < 15)].sum()
        high_band = psd[freqs >= 15].sum()
        
        total_energy = psd.sum()
        if total_energy > 0:
            features["low_band_energy"] = float(low_band / total_energy)
            features["mid_band_energy"] = float(mid_band / total_energy)
            features["high_band_energy"] = float(high_band / total_energy)
        
        # Sway calculation (simplified)
        # In production, would use proper biomechanical models
        features["sway_ap"] = float(np.std(acceleration[:, 0]))  # Anterior-posterior
        features["sway_ml"] = float(np.std(acceleration[:, 1]))  # Medial-lateral
        
        return features
    
    @staticmethod
    def calculate_fatigue_features(
        training_history: List[Dict],
        current_hrv: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate fatigue-related features"""
        
        if not training_history:
            return {"fatigue_index": 0.5, "recovery_score": 0.5}
        
        # Calculate training load (simplified TRIMP)
        recent_load = sum(
            session.get("training_load", 0) 
            for session in training_history[-7:]  # Last 7 sessions
        )
        
        # HRV trend
        if len(training_history) > 3:
            recent_hrv = [s.get("hrv_rmssd", 50) for s in training_history[-3:]]
            hrv_trend = (current_hrv.get("rMSSD", 50) - np.mean(recent_hrv)) / np.mean(recent_hrv)
        else:
            hrv_trend = 0
        
        # Simple fatigue model
        fatigue_index = min(1.0, recent_load / 5000)  # Normalize by typical weekly load
        recovery_score = max(0, min(1.0, 0.5 + hrv_trend))
        
        return {
            "fatigue_index": float(fatigue_index),
            "recovery_score": float(recovery_score),
            "training_load_7d": float(recent_load),
            "hrv_trend": float(hrv_trend)
        }
    
    @staticmethod
    def create_shooting_features(
        heart_rate: float,
        hrv: Dict[str, float],
        body_sway: Dict[str, float],
        wind: Dict[str, float],
        athlete_profile: Dict[str, Any]
    ) -> np.ndarray:
        """Create feature vector for shooting prediction"""
        
        hr_max = athlete_profile.get("hr_max", 195)
        
        features = [
            heart_rate / hr_max,  # HR percentage
            hrv.get("rMSSD", 30) / 100,  # Normalized HRV
            body_sway.get("ap", 0.5),  # AP sway
            body_sway.get("ml", 0.5),  # ML sway
            wind.get("speed", 0) / 10,  # Normalized wind speed
            np.sin(np.radians(wind.get("direction", 0))),  # Wind direction X
            np.cos(np.radians(wind.get("direction", 0))),  # Wind direction Y
        ]
        
        return np.array(features).reshape(1, -1)
