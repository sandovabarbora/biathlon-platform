"""Training pipeline for ML models"""
import logging
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import optuna
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sensor_data import SensorData
from app.models.prediction import Prediction
from app.models.athlete import Athlete

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Model training pipeline"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def train_shooting_model(
        self, 
        athlete_id: Optional[int] = None,
        days_back: int = 90
    ) -> Dict[str, Any]:
        """Train shooting accuracy model"""
        
        # Fetch training data
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(Prediction).where(
            Prediction.prediction_type == "shooting",
            Prediction.actual_value.isnot(None),
            Prediction.timestamp >= start_date
        )
        
        if athlete_id:
            query = query.where(Prediction.athlete_id == athlete_id)
        
        result = await self.db.execute(query)
        predictions = result.scalars().all()
        
        if len(predictions) < 100:
            logger.warning("Not enough data for training")
            return {"status": "insufficient_data", "samples": len(predictions)}
        
        # Prepare features and targets
        features = []
        targets = []
        
        for pred in predictions:
            factors = pred.contributing_factors
            features.append([
                factors.get("heart_rate", 1.0),
                factors.get("lactate", 1.0),
                factors.get("fatigue", 1.0),
                factors.get("stability", 1.0),
                factors.get("wind", 1.0)
            ])
            targets.append(pred.actual_value)
        
        X = np.array(features)
        y = np.array(targets)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Hyperparameter optimization with Optuna
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            }
            
            model = xgb.XGBRegressor(**params, random_state=42)
            scores = cross_val_score(
                model, X_train, y_train, 
                cv=5, scoring='neg_mean_absolute_error'
            )
            return -scores.mean()
        
        # Optimize
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=50, show_progress_bar=False)
        
        # Train final model with best params
        best_params = study.best_params
        model = xgb.XGBRegressor(**best_params, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Feature importance
        importance = model.feature_importances_
        feature_names = ["heart_rate", "lactate", "fatigue", "stability", "wind"]
        feature_importance = dict(zip(feature_names, importance))
        
        # Save model
        import joblib
        from pathlib import Path
        model_path = Path(settings.MODEL_PATH) / f"shooting_model_{athlete_id or 'global'}.pkl"
        joblib.dump(model, model_path)
        
        return {
            "status": "success",
            "samples": len(predictions),
            "mae": float(mae),
            "r2": float(r2),
            "best_params": best_params,
            "feature_importance": feature_importance,
            "model_path": str(model_path)
        }
    
    async def train_lactate_model(
        self,
        athlete_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Train personalized lactate model"""
        
        # Fetch athlete data
        athlete = await self.db.get(Athlete, athlete_id)
        if not athlete:
            raise ValueError("Athlete not found")
        
        # Fetch sensor data with lactate measurements
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        query = select(SensorData).where(
            SensorData.athlete_id == athlete_id,
            SensorData.timestamp >= start_date,
            SensorData.lactate_estimated.isnot(None)
        )
        
        result = await self.db.execute(query)
        sensor_data = result.scalars().all()
        
        if len(sensor_data) < 50:
            return {"status": "insufficient_data", "samples": len(sensor_data)}
        
        # Prepare features
        features = []
        targets = []
        
        for data in sensor_data:
            if data.heart_rate and data.heart_rate_variability:
                features.append([
                    data.heart_rate,
                    data.heart_rate_variability.get("rMSSD", 30),
                    (data.timestamp - sensor_data[0].timestamp).total_seconds(),
                    data.energy_expenditure or 200
                ])
                targets.append(data.lactate_estimated)
        
        X = np.array(features)
        y = np.array(targets)
        
        # Train personalized model
        from sklearn.ensemble import GradientBoostingRegressor
        
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        )
        
        # Cross-validation
        scores = cross_val_score(
            model, X, y, cv=5, 
            scoring='neg_mean_absolute_error'
        )
        
        # Train final model
        model.fit(X, y)
        
        # Save model
        import joblib
        from pathlib import Path
        model_path = Path(settings.MODEL_PATH) / f"lactate_model_{athlete_id}.pkl"
        joblib.dump(model, model_path)
        
        return {
            "status": "success",
            "samples": len(sensor_data),
            "cv_mae": float(-scores.mean()),
            "cv_std": float(scores.std()),
            "model_path": str(model_path)
        }
