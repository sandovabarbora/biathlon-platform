"""ML Model Manager for loading and serving models"""
import logging
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import joblib

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """Singleton model manager"""
    _instance = None
    _models: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def load_models(cls) -> None:
        """Load all ML models"""
        instance = cls()
        model_path = Path(settings.MODEL_PATH)
        
        try:
            # Load shooting accuracy model
            shooting_model_path = model_path / "shooting_model.pkl"
            if shooting_model_path.exists():
                instance._models["shooting"] = joblib.load(shooting_model_path)
                logger.info("Loaded shooting model")
            else:
                # Create default model if not exists
                instance._models["shooting"] = instance._create_default_shooting_model()
                logger.info("Created default shooting model")
            
            # Load lactate model
            lactate_model_path = model_path / "lactate_model.pkl"
            if lactate_model_path.exists():
                instance._models["lactate"] = joblib.load(lactate_model_path)
                logger.info("Loaded lactate model")
            else:
                instance._models["lactate"] = instance._create_default_lactate_model()
                logger.info("Created default lactate model")
            
            # Load fatigue model
            fatigue_model_path = model_path / "fatigue_model.pkl"
            if fatigue_model_path.exists():
                instance._models["fatigue"] = joblib.load(fatigue_model_path)
                logger.info("Loaded fatigue model")
            else:
                instance._models["fatigue"] = instance._create_default_fatigue_model()
                logger.info("Created default fatigue model")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    @classmethod
    def get_model(cls, model_name: str) -> Any:
        """Get specific model"""
        instance = cls()
        return instance._models.get(model_name)
    
    @classmethod
    def predict(cls, model_name: str, features: np.ndarray) -> np.ndarray:
        """Make prediction with specific model"""
        model = cls.get_model(model_name)
        if model is None:
            raise ValueError(f"Model {model_name} not loaded")
        return model.predict(features)
    
    @classmethod
    def cleanup(cls) -> None:
        """Cleanup models from memory"""
        instance = cls()
        instance._models.clear()
        logger.info("Models cleaned up")
    
    def _create_default_shooting_model(self) -> Any:
        """Create default shooting accuracy model"""
        # Features: hr_pct, lactate, fatigue, stability, wind
        model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='reg:squarederror',
            random_state=42
        )
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Feature generation
        hr_pct = np.random.uniform(0.7, 0.95, n_samples)
        lactate = np.random.uniform(1, 8, n_samples)
        fatigue = np.random.uniform(0, 1, n_samples)
        stability = np.random.uniform(0.3, 1.5, n_samples)
        wind = np.random.uniform(0, 5, n_samples)
        
        X = np.column_stack([hr_pct, lactate, fatigue, stability, wind])
        
        # Target generation (shooting accuracy)
        y = (
            0.95 - 
            0.2 * np.maximum(0, hr_pct - 0.87) -  # HR penalty
            0.05 * np.maximum(0, lactate - 4) -   # Lactate penalty
            0.1 * fatigue -                       # Fatigue penalty
            0.1 * stability -                      # Stability penalty
            0.02 * wind +                         # Wind penalty
            np.random.normal(0, 0.02, n_samples)  # Noise
        )
        y = np.clip(y, 0.5, 1.0)
        
        # Train model
        model.fit(X, y)
        
        # Save model
        model_path = Path(settings.MODEL_PATH)
        model_path.mkdir(exist_ok=True)
        joblib.dump(model, model_path / "shooting_model.pkl")
        
        return model
    
    def _create_default_lactate_model(self) -> Any:
        """Create default lactate estimation model"""
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        )
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: heart_rate, hrv_rmssd, duration, power
        heart_rate = np.random.uniform(100, 190, n_samples)
        hrv_rmssd = np.random.uniform(10, 60, n_samples)
        duration = np.random.uniform(0, 3600, n_samples)  # seconds
        power = np.random.uniform(100, 400, n_samples)  # watts
        
        X = np.column_stack([heart_rate, hrv_rmssd, duration, power])
        
        # Target generation (lactate)
        hr_zones = heart_rate / 195  # Assuming max HR of 195
        y = (
            1.0 +
            3.0 * np.power(hr_zones, 2) +
            0.001 * duration +
            0.005 * power -
            0.02 * hrv_rmssd +
            np.random.normal(0, 0.3, n_samples)
        )
        y = np.clip(y, 0.5, 15.0)
        
        # Train model
        model.fit(X, y)
        
        # Save model
        model_path = Path(settings.MODEL_PATH)
        model_path.mkdir(exist_ok=True)
        joblib.dump(model, model_path / "lactate_model.pkl")
        
        return model
    
    def _create_default_fatigue_model(self) -> Any:
        """Create default fatigue model"""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: training_load, sleep_quality, hrv_trend, time_since_rest
        training_load = np.random.uniform(0, 1000, n_samples)  # TRIMP
        sleep_quality = np.random.uniform(3, 10, n_samples)
        hrv_trend = np.random.uniform(-20, 20, n_samples)  # % change
        time_since_rest = np.random.uniform(0, 72, n_samples)  # hours
        
        X = np.column_stack([training_load, sleep_quality, hrv_trend, time_since_rest])
        
        # Target generation (fatigue index 0-1)
        y = (
            0.2 +
            0.0005 * training_load +
            0.01 * time_since_rest -
            0.05 * sleep_quality -
            0.01 * hrv_trend +
            np.random.normal(0, 0.05, n_samples)
        )
        y = np.clip(y, 0, 1)
        
        # Train model
        model.fit(X, y)
        
        # Save model
        model_path = Path(settings.MODEL_PATH)
        model_path.mkdir(exist_ok=True)
        joblib.dump(model, model_path / "fatigue_model.pkl")
        
        return model
