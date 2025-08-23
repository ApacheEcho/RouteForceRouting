"""
RouteForce Advanced Analytics & AI Insights Module
Provides predictive analytics, route intelligence, and business insights
"""

import logging
import os
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (GradientBoostingRegressor, IsolationForest,
                              RandomForestRegressor, VotingRegressor)
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import (GridSearchCV, TimeSeriesSplit,
                                     cross_val_score, cross_validate,
                                     train_test_split)
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler, StandardScaler

warnings.filterwarnings("ignore")

# Import database integration service
from app.services.database_integration import database_service

logger = logging.getLogger(__name__)


import xgboost as xgb
from scipy import stats
# Add advanced ML imports for enhanced capabilities
from sklearn.ensemble import AdaBoostRegressor, ExtraTreesRegressor
from sklearn.linear_model import ElasticNet, HuberRegressor
from sklearn.svm import SVR


@dataclass
class RouteInsight:
    """Route performance insight"""

    route_id: str
    insight_type: str
    title: str
    description: str
    impact_score: float  # 0-100
    confidence: float  # 0-1
    recommendations: list[str]
    metrics: dict[str, Any]
    timestamp: str


@dataclass
class PredictionResult:
    """Route prediction result"""

    route_id: str
    predicted_duration: float
    predicted_fuel_cost: float
    confidence_interval: tuple[float, float]
    risk_factors: list[str]
    optimization_suggestions: list[str]


@dataclass
class PerformanceTrend:
    """Performance trend analysis"""

    metric_name: str
    current_value: float
    trend_direction: str  # 'improving', 'declining', 'stable'
    change_percentage: float
    forecast_7d: float
    forecast_30d: float


@dataclass
class UncertaintyQuantification:
    """Uncertainty quantification for predictions"""

    mean_prediction: float
    std_prediction: float
    confidence_interval_95: tuple[float, float]
    prediction_intervals: dict[str, tuple[float, float]]
    model_confidence: float
    epistemic_uncertainty: float  # Model uncertainty
    aleatoric_uncertainty: float  # Data uncertainty


@dataclass
class AdvancedPredictionResult:
    """Advanced prediction result with uncertainty quantification"""

    route_id: str
    predicted_duration: float
    predicted_fuel_cost: float
    uncertainty: UncertaintyQuantification
    risk_factors: list[str]
    optimization_suggestions: list[str]
    feature_importance: dict[str, float]
    model_explainability: dict[str, Any]


class AdvancedAnalytics:
    """Advanced analytics engine for route optimization insights"""

    def __init__(self):
        self.route_predictor = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.historical_data = []
        self.insights_cache = {}
        self.feature_columns = []  # Store consistent feature columns
        self.db_service = database_service  # Database integration

        # Initialize advanced ensemble engine
        self.ensemble_engine = None  # Will be initialized later
        self.advanced_models_trained = False

    def add_route_data(self, route_data: dict[str, Any]) -> None:
        """Add route performance data for analysis and store in database"""
        enriched_data = self._enrich_route_data(route_data)
        self.historical_data.append(enriched_data)

        # Store in database
        try:
            route_id = self.db_service.store_route_data(enriched_data)
            enriched_data["route_id"] = route_id
            logger.info(f"Stored route data in database: {route_id}")
        except Exception as e:
            logger.error(f"Failed to store route data: {str(e)}")

        # Retrain models periodically
        if len(self.historical_data) % 50 == 0:
            self._train_models()

        # Train advanced ensemble every 100 samples
        if len(self.historical_data) % 100 == 0 and len(self.historical_data) >= 200:
            self._train_advanced_ensemble()

    def load_historical_data(self, days_back: int = 30) -> None:
        """Load historical route data from database"""
        try:
            historical_routes = self.db_service.get_historical_routes(
                days_back=days_back
            )
            self.historical_data = historical_routes
            logger.info(
                f"Loaded {len(historical_routes)} historical routes from database"
            )

            # Train models with loaded data
            if len(self.historical_data) > 10:
                self._train_models()

            # Train advanced ensemble if sufficient data
            if len(self.historical_data) >= 200:
                self._train_advanced_ensemble()

        except Exception as e:
            logger.error(f"Failed to load historical data: {str(e)}")

    def get_insights_from_database(
        self, route_id: str | None = None, days_back: int = 30
    ) -> list[dict[str, Any]]:
        """Retrieve insights from database"""
        try:
            return self.db_service.get_route_insights(
                route_id=route_id, days_back=days_back
            )
        except Exception as e:
            logger.error(f"Failed to retrieve insights: {str(e)}")
            return []

    def get_performance_metrics_from_database(
        self, days_back: int = 30
    ) -> dict[str, Any]:
        """Get performance metrics from database"""
        try:
            return self.db_service.get_performance_metrics(days_back=days_back)
        except Exception as e:
            logger.error(f"Failed to retrieve performance metrics: {str(e)}")
            return {}

    def _enrich_route_data(self, route_data: dict[str, Any]) -> dict[str, Any]:
        """Enrich route data with calculated features"""
        enriched = route_data.copy()

        # Calculate efficiency metrics
        if "distance" in route_data and "duration" in route_data:
            enriched["speed_avg"] = route_data["distance"] / max(
                route_data["duration"], 1
            )

        if "fuel_used" in route_data and "distance" in route_data:
            enriched["fuel_efficiency"] = route_data["distance"] / max(
                route_data["fuel_used"], 0.1
            )

        # Time-based features
        if "timestamp" in route_data:
            dt = datetime.fromisoformat(route_data["timestamp"])
            enriched["hour_of_day"] = dt.hour
            enriched["day_of_week"] = dt.weekday()
            enriched["is_weekend"] = dt.weekday() >= 5
            enriched["is_rush_hour"] = dt.hour in [7, 8, 9, 17, 18, 19]

        # Route complexity
        if "stops" in route_data:
            enriched["stops_count"] = len(route_data["stops"])
            enriched["avg_stop_distance"] = route_data.get("distance", 0) / max(
                len(route_data["stops"]), 1
            )

        return enriched

    def _train_models(self) -> None:
        """Train predictive models on historical data"""
        if len(self.historical_data) < 10:
            return

        df = pd.DataFrame(self.historical_data)

        # Prepare features for duration prediction
        feature_columns = [
            "distance",
            "stops_count",
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "is_rush_hour",
            "avg_stop_distance",
        ]

        # Filter available features and ensure consistency
        available_features = [col for col in feature_columns if col in df.columns]

        if len(available_features) < 3 or "duration" not in df.columns:
            return

        # Store the feature columns for consistent prediction
        self.feature_columns = available_features

        X = df[available_features].fillna(0)
        y_duration = df["duration"].fillna(df["duration"].mean())

        # Train duration predictor
        if len(X) > 5:
            X_scaled = self.scaler.fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_duration, test_size=0.2, random_state=42
            )

            self.route_predictor = RandomForestRegressor(
                n_estimators=100, random_state=42, max_depth=10
            )
            self.route_predictor.fit(X_train, y_train)

            # Train anomaly detector
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.anomaly_detector.fit(X_scaled)

    def _train_advanced_ensemble(self) -> None:
        """Train advanced ensemble models with uncertainty quantification"""
        if len(self.historical_data) < 200:
            logger.info(
                "Insufficient data for advanced ensemble training (need 200+ samples)"
            )
            return

        try:
            df = pd.DataFrame(self.historical_data)

            # Enhanced feature engineering
            feature_columns = [
                "distance",
                "stops_count",
                "hour_of_day",
                "day_of_week",
                "is_weekend",
                "is_rush_hour",
                "avg_stop_distance",
            ]

            # Add interaction features
            if all(col in df.columns for col in ["distance", "stops_count"]):
                df["distance_per_stop"] = df["distance"] / np.maximum(
                    df["stops_count"], 1
                )
                df["complexity_score"] = df["distance"] * df["stops_count"]
                feature_columns.extend(["distance_per_stop", "complexity_score"])

            # Time-based features
            if "hour_of_day" in df.columns:
                df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
                df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
                feature_columns.extend(["hour_sin", "hour_cos"])

            # Filter available features
            available_features = [col for col in feature_columns if col in df.columns]

            if len(available_features) < 5 or "duration" not in df.columns:
                logger.warning("Insufficient features for advanced ensemble training")
                return

            X = df[available_features].fillna(0).values
            y = df["duration"].fillna(df["duration"].mean()).values

            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            # Train advanced ensemble
            training_results = self.ensemble_engine.train_ensemble_with_uncertainty(
                X_scaled, y
            )

            self.advanced_models_trained = True
            self.feature_columns = available_features

            logger.info(
                f"Advanced ensemble trained successfully with {len(training_results['trained_models'])} models"
            )

        except Exception as e:
            logger.error(f"Failed to train advanced ensemble: {str(e)}")

    def predict_route_performance(
        self, route_features: dict[str, Any]
    ) -> PredictionResult:
        """Predict route performance metrics"""
        if not self.route_predictor or not hasattr(self, "feature_columns"):
            # Return default prediction if model not trained
            return PredictionResult(
                route_id=route_features.get("route_id", "unknown"),
                predicted_duration=route_features.get("distance", 10)
                * 0.05,  # Default: 3 min per km
                predicted_fuel_cost=route_features.get("distance", 10)
                * 0.12,  # Default: $0.12 per km
                confidence_interval=(0.8, 1.2),
                risk_factors=["Model not trained - using default estimates"],
                optimization_suggestions=[
                    "Collect more route data for better predictions"
                ],
            )

        # Use the same feature columns as training
        features = []
        for col in self.feature_columns:
            if col in route_features:
                features.append(route_features[col])
            else:
                # Use reasonable defaults
                defaults = {
                    "distance": 10,
                    "stops_count": 5,
                    "hour_of_day": 10,
                    "day_of_week": 2,
                    "is_weekend": 0,
                    "is_rush_hour": 0,
                    "avg_stop_distance": 2,
                }
                features.append(defaults.get(col, 0))

        # Make prediction
        X = np.array([features])
        X_scaled = self.scaler.transform(X)

        predicted_duration = self.route_predictor.predict(X_scaled)[0]

        # Calculate fuel cost (simple model)
        distance = route_features.get("distance", 10)
        fuel_efficiency = 8.5  # km per liter average
        fuel_price = 1.45  # $ per liter
        predicted_fuel_cost = (distance / fuel_efficiency) * fuel_price

        # Detect anomalies/risk factors
        risk_factors = []
        if self.anomaly_detector:
            anomaly_score = self.anomaly_detector.decision_function(X_scaled)[0]
            if anomaly_score < -0.1:
                risk_factors.append("Route parameters unusual - higher uncertainty")

        # Add context-based risk factors
        if route_features.get("is_rush_hour", False):
            risk_factors.append("Rush hour traffic may cause delays")

        if route_features.get("stops_count", 0) > 10:
            risk_factors.append("High number of stops may increase complexity")

        # Generate optimization suggestions
        suggestions = []
        if route_features.get("hour_of_day", 10) in [7, 8, 17, 18]:
            suggestions.append("Consider scheduling outside rush hours")

        if route_features.get("stops_count", 0) > 8:
            suggestions.append("Consider splitting into multiple routes")

        # Confidence interval (simplified)
        confidence_range = max(0.1, abs(predicted_duration * 0.15))
        confidence_interval = (
            predicted_duration - confidence_range,
            predicted_duration + confidence_range,
        )

        return PredictionResult(
            route_id=route_features.get("route_id", "unknown"),
            predicted_duration=predicted_duration,
            predicted_fuel_cost=predicted_fuel_cost,
            confidence_interval=confidence_interval,
            risk_factors=risk_factors,
            optimization_suggestions=suggestions,
        )

    def analyze_route_efficiency(
        self, route_id: str, route_data: dict[str, Any]
    ) -> RouteInsight:
        """Analyze route efficiency and generate insights"""

        # Calculate efficiency metrics
        distance = route_data.get("distance", 0)
        duration = route_data.get("duration", 1)
        stops = route_data.get("stops", [])

        # Basic efficiency calculations
        speed_avg = distance / max(duration, 0.1) * 60  # km/h
        time_per_stop = duration / max(len(stops), 1)

        # Determine insight type and recommendations
        if speed_avg < 20:
            insight_type = "efficiency_warning"
            title = "Low Average Speed Detected"
            description = f"Route {route_id} has an average speed of {speed_avg:.1f} km/h, which is below optimal."
            impact_score = 75
            recommendations = [
                "Review route for traffic congestion points",
                "Consider alternative time windows",
                "Optimize stop sequence to reduce backtracking",
            ]
        elif time_per_stop > 15:
            insight_type = "stop_optimization"
            title = "High Time Per Stop"
            description = f"Average {time_per_stop:.1f} minutes per stop. Consider optimizing stop procedures."
            impact_score = 60
            recommendations = [
                "Standardize delivery procedures",
                "Pre-sort packages by delivery order",
                "Use mobile scanning for faster check-ins",
            ]
        else:
            insight_type = "performance_good"
            title = "Good Route Performance"
            description = (
                f"Route {route_id} is performing well with good efficiency metrics."
            )
            impact_score = 30
            recommendations = [
                "Maintain current procedures",
                "Consider this route as a template for similar routes",
            ]

        insight = RouteInsight(
            route_id=route_id,
            insight_type=insight_type,
            title=title,
            description=description,
            impact_score=impact_score,
            confidence=0.85,
            recommendations=recommendations,
            metrics={
                "avg_speed_kmh": speed_avg,
                "time_per_stop_min": time_per_stop,
                "total_distance_km": distance,
                "total_duration_min": duration,
                "stops_count": len(stops),
            },
            timestamp=datetime.now().isoformat(),
        )

        # Store insight in database
        try:
            insight_data = {
                "type": insight_type,
                "category": "performance",
                "title": title,
                "description": description,
                "severity": (
                    "high"
                    if impact_score > 70
                    else "medium" if impact_score > 40 else "low"
                ),
                "confidence": 0.85,
                "impact": impact_score,
                "actionable": True,
                "recommendation": "; ".join(recommendations),
                "data_points": insight.metrics,
            }
            self.db_service.store_route_insights(route_id, [insight_data])
            logger.info(f"Stored insight for route {route_id}: {insight_type}")
        except Exception as e:
            logger.error(f"Failed to store insight: {str(e)}")

        return insight

    def detect_performance_trends(
        self, timeframe_days: int = 30
    ) -> list[PerformanceTrend]:
        """Detect performance trends over time"""
        if len(self.historical_data) < 10:
            return []

        df = pd.DataFrame(self.historical_data)

        # Filter recent data
        if "timestamp" in df.columns:
            df["date"] = pd.to_datetime(df["timestamp"])
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            df = df[df["date"] >= cutoff_date]

        trends = []

        # Analyze efficiency trend
        if "fuel_efficiency" in df.columns and len(df) > 5:
            recent_efficiency = df["fuel_efficiency"].tail(10).mean()
            older_efficiency = df["fuel_efficiency"].head(10).mean()
            change_pct = (
                (recent_efficiency - older_efficiency) / older_efficiency
            ) * 100

            trend_direction = "stable"
            if change_pct > 5:
                trend_direction = "improving"
            elif change_pct < -5:
                trend_direction = "declining"

            trends.append(
                PerformanceTrend(
                    metric_name="Fuel Efficiency",
                    current_value=recent_efficiency,
                    trend_direction=trend_direction,
                    change_percentage=change_pct,
                    forecast_7d=recent_efficiency * (1 + change_pct / 100 * 0.25),
                    forecast_30d=recent_efficiency * (1 + change_pct / 100),
                )
            )

        # Analyze duration trend
        if "duration" in df.columns and len(df) > 5:
            recent_duration = df["duration"].tail(10).mean()
            older_duration = df["duration"].head(10).mean()
            change_pct = ((recent_duration - older_duration) / older_duration) * 100

            trend_direction = "stable"
            if change_pct < -5:  # Lower duration is better
                trend_direction = "improving"
            elif change_pct > 5:
                trend_direction = "declining"

            trends.append(
                PerformanceTrend(
                    metric_name="Average Duration",
                    current_value=recent_duration,
                    trend_direction=trend_direction,
                    change_percentage=change_pct,
                    forecast_7d=recent_duration * (1 + change_pct / 100 * 0.25),
                    forecast_30d=recent_duration * (1 + change_pct / 100),
                )
            )

        return trends

    def get_fleet_insights(self) -> dict[str, Any]:
        """Generate comprehensive fleet insights"""
        if len(self.historical_data) < 5:
            return {
                "total_routes": 0,
                "insights": [],
                "trends": [],
                "recommendations": [
                    "Collect more route data for comprehensive insights"
                ],
            }

        df = pd.DataFrame(self.historical_data)

        # Calculate fleet-wide metrics
        total_routes = len(df)
        avg_efficiency = df.get("fuel_efficiency", pd.Series([0])).mean()
        avg_duration = df.get("duration", pd.Series([0])).mean()

        # Generate top insights
        insights = []
        trends = self.detect_performance_trends()

        # Fleet-wide recommendations
        recommendations = []
        if avg_efficiency < 10:
            recommendations.append("Consider fuel efficiency training for drivers")
        if avg_duration > 120:
            recommendations.append("Review route optimization algorithms")

        recommendations.extend(
            [
                "Implement predictive maintenance schedules",
                "Consider route consolidation opportunities",
                "Monitor weather impact on performance",
            ]
        )

        return {
            "total_routes": total_routes,
            "avg_fuel_efficiency": avg_efficiency,
            "avg_duration_minutes": avg_duration,
            "insights": [asdict(insight) for insight in insights],
            "trends": [asdict(trend) for trend in trends],
            "recommendations": recommendations,
            "last_updated": datetime.now().isoformat(),
        }


class AdvancedMLModels:
    """Advanced ML models for route prediction and optimization"""

    def __init__(self):
        self.duration_model = None
        self.fuel_model = None
        self.ensemble_model = None
        self.feature_selector = None
        self.scaler = RobustScaler()
        self.model_metadata = {}

    def create_ensemble_model(self) -> VotingRegressor:
        """Create ensemble model with multiple algorithms"""

        # Base models
        rf_model = RandomForestRegressor(
            n_estimators=200, max_depth=15, min_samples_split=5, random_state=42
        )

        gb_model = GradientBoostingRegressor(
            n_estimators=150, learning_rate=0.1, max_depth=8, random_state=42
        )

        nn_model = MLPRegressor(
            hidden_layer_sizes=(100, 50, 25),
            activation="relu",
            alpha=0.01,
            max_iter=1000,
            random_state=42,
        )

        # Create ensemble
        ensemble = VotingRegressor(
            [("rf", rf_model), ("gb", gb_model), ("nn", nn_model)]
        )

        return ensemble

    def optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray) -> dict[str, Any]:
        """Optimize model hyperparameters using grid search"""

        param_grid = {
            "rf__n_estimators": [100, 200, 300],
            "rf__max_depth": [10, 15, 20],
            "gb__n_estimators": [100, 150, 200],
            "gb__learning_rate": [0.05, 0.1, 0.2],
            "nn__hidden_layer_sizes": [(50, 25), (100, 50), (100, 50, 25)],
        }

        ensemble = self.create_ensemble_model()

        # Perform grid search
        grid_search = GridSearchCV(
            ensemble,
            param_grid,
            cv=5,
            scoring="neg_mean_squared_error",
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X, y)

        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best cross-validation score: {grid_search.best_score_}")

        return {
            "best_model": grid_search.best_estimator_,
            "best_params": grid_search.best_params_,
            "best_score": grid_search.best_score_,
            "cv_results": grid_search.cv_results_,
        }

    def feature_engineering_advanced(self, df: pd.DataFrame) -> pd.DataFrame:
        """Advanced feature engineering with domain knowledge"""

        enhanced_df = df.copy()

        # Interaction features
        if "distance" in df.columns and "stops_count" in df.columns:
            enhanced_df["distance_per_stop"] = df["distance"] / np.maximum(
                df["stops_count"], 1
            )
            enhanced_df["complexity_score"] = df["distance"] * df["stops_count"]

        # Time-based features
        if "hour_of_day" in df.columns:
            enhanced_df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
            enhanced_df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
            enhanced_df["is_peak_morning"] = (
                (df["hour_of_day"] >= 7) & (df["hour_of_day"] <= 9)
            ).astype(int)
            enhanced_df["is_peak_evening"] = (
                (df["hour_of_day"] >= 17) & (df["hour_of_day"] <= 19)
            ).astype(int)

        # Weather simulation (placeholder for real weather data)
        enhanced_df["weather_impact"] = np.random.normal(1.0, 0.1, len(df))
        enhanced_df["traffic_density"] = np.random.uniform(0.5, 1.5, len(df))

        # Vehicle efficiency factors
        if "vehicle_type" in df.columns:
            vehicle_efficiency = {"car": 1.0, "van": 0.8, "truck": 0.6}
            enhanced_df["vehicle_efficiency"] = (
                df["vehicle_type"].map(vehicle_efficiency).fillna(1.0)
            )

        # Driver experience simulation
        if "driver_id" in df.columns:
            driver_count = df["driver_id"].value_counts()
            enhanced_df["driver_experience"] = (
                df["driver_id"].map(driver_count).fillna(1)
            )
            enhanced_df["driver_experience_normalized"] = (
                enhanced_df["driver_experience"]
                / enhanced_df["driver_experience"].max()
            )

        return enhanced_df

    def train_advanced_models(
        self, historical_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Train advanced ML models with enhanced features"""

        if len(historical_data) < 50:
            logger.warning("Insufficient data for advanced model training")
            return {"status": "insufficient_data"}

        # Convert to DataFrame
        df = pd.DataFrame(historical_data)

        # Advanced feature engineering
        df_enhanced = self.feature_engineering_advanced(df)

        # Feature columns for prediction
        feature_columns = [
            "distance",
            "stops_count",
            "hour_of_day",
            "day_of_week",
            "is_weekend",
            "is_rush_hour",
            "distance_per_stop",
            "complexity_score",
            "hour_sin",
            "hour_cos",
            "is_peak_morning",
            "is_peak_evening",
            "weather_impact",
            "traffic_density",
            "vehicle_efficiency",
            "driver_experience_normalized",
        ]

        # Filter available features
        available_features = [
            col for col in feature_columns if col in df_enhanced.columns
        ]

        if len(available_features) < 5:
            logger.warning("Insufficient features for advanced model training")
            return {"status": "insufficient_features"}

        # Prepare data
        X = df_enhanced[available_features].fillna(0)
        y_duration = df_enhanced["duration"].fillna(df_enhanced["duration"].mean())

        # Feature selection
        self.feature_selector = SelectKBest(
            score_func=f_regression, k=min(10, len(available_features))
        )
        X_selected = self.feature_selector.fit_transform(X, y_duration)

        # Scale features
        X_scaled = self.scaler.fit_transform(X_selected)

        # Optimize and train ensemble model
        optimization_results = self.optimize_hyperparameters(X_scaled, y_duration)
        self.duration_model = optimization_results["best_model"]

        # Cross-validation scores
        cv_scores = cross_val_score(
            self.duration_model,
            X_scaled,
            y_duration,
            cv=5,
            scoring="neg_mean_squared_error",
        )

        # Train fuel consumption model separately
        if "fuel_used" in df_enhanced.columns:
            y_fuel = df_enhanced["fuel_used"].fillna(df_enhanced["fuel_used"].mean())
            self.fuel_model = GradientBoostingRegressor(
                n_estimators=200, random_state=42
            )
            self.fuel_model.fit(X_scaled, y_fuel)

        # Store metadata
        self.model_metadata = {
            "training_samples": len(df_enhanced),
            "features_used": available_features,
            "selected_features": self.feature_selector.get_feature_names_out(
                available_features
            ).tolist(),
            "cv_mean_score": -cv_scores.mean(),
            "cv_std_score": cv_scores.std(),
            "best_params": optimization_results["best_params"],
            "training_timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"Advanced models trained successfully. CV Score: {-cv_scores.mean():.3f} ± {cv_scores.std():.3f}"
        )

        return {
            "status": "success",
            "metadata": self.model_metadata,
            "cv_scores": cv_scores.tolist(),
        }

    def predict_with_uncertainty(
        self, route_features: dict[str, Any]
    ) -> dict[str, Any]:
        """Make predictions with uncertainty quantification"""

        if not self.duration_model:
            return {"status": "model_not_trained"}

        # Enhance features
        df_single = pd.DataFrame([route_features])
        df_enhanced = self.feature_engineering_advanced(df_single)

        # Use same features as training
        available_features = self.model_metadata["features_used"]

        # Prepare features
        features = []
        for col in available_features:
            if col in df_enhanced.columns:
                features.append(df_enhanced[col].iloc[0])
            else:
                defaults = {
                    "distance": 10,
                    "stops_count": 5,
                    "hour_of_day": 10,
                    "day_of_week": 2,
                    "is_weekend": 0,
                    "is_rush_hour": 0,
                    "distance_per_stop": 2,
                    "complexity_score": 50,
                    "hour_sin": 0,
                    "hour_cos": 1,
                    "is_peak_morning": 0,
                    "is_peak_evening": 0,
                    "weather_impact": 1.0,
                    "traffic_density": 1.0,
                    "vehicle_efficiency": 1.0,
                    "driver_experience_normalized": 0.5,
                }
                features.append(defaults.get(col, 0))

        # Transform features
        X = np.array([features])
        X_selected = self.feature_selector.transform(X)
        X_scaled = self.scaler.transform(X_selected)

        # Duration prediction with uncertainty
        if hasattr(self.duration_model, "estimators_"):
            # For ensemble models, get predictions from all estimators
            individual_predictions = []
            for estimator in self.duration_model.estimators_:
                pred = estimator.predict(X_scaled)[0]
                individual_predictions.append(pred)

            duration_pred = np.mean(individual_predictions)
            duration_std = np.std(individual_predictions)
            confidence_interval = (
                duration_pred - 1.96 * duration_std,
                duration_pred + 1.96 * duration_std,
            )
        else:
            duration_pred = self.duration_model.predict(X_scaled)[0]
            # Use cross-validation std as uncertainty estimate
            duration_std = self.model_metadata.get("cv_std_score", duration_pred * 0.1)
            confidence_interval = (
                duration_pred - 1.96 * duration_std,
                duration_pred + 1.96 * duration_std,
            )

        # Fuel prediction
        fuel_pred = None
        if self.fuel_model:
            fuel_pred = self.fuel_model.predict(X_scaled)[0]

        return {
            "status": "success",
            "predicted_duration": float(duration_pred),
            "duration_uncertainty": float(duration_std),
            "confidence_interval": confidence_interval,
            "predicted_fuel": float(fuel_pred) if fuel_pred else None,
            "model_confidence": float(1.0 / (1.0 + duration_std)),
            "features_used": len(available_features),
        }

    def save_models(self, model_dir: str = "models"):
        """Save trained models to disk"""
        os.makedirs(model_dir, exist_ok=True)

        if self.duration_model:
            joblib.dump(
                self.duration_model, os.path.join(model_dir, "duration_model.pkl")
            )
        if self.fuel_model:
            joblib.dump(self.fuel_model, os.path.join(model_dir, "fuel_model.pkl"))
        if self.feature_selector:
            joblib.dump(
                self.feature_selector, os.path.join(model_dir, "feature_selector.pkl")
            )

        joblib.dump(self.scaler, os.path.join(model_dir, "scaler.pkl"))
        joblib.dump(self.model_metadata, os.path.join(model_dir, "metadata.pkl"))

        logger.info(f"Models saved to {model_dir}")

    def load_models(self, model_dir: str = "models"):
        """Load trained models from disk"""
        try:
            self.duration_model = joblib.load(
                os.path.join(model_dir, "duration_model.pkl")
            )
            self.fuel_model = joblib.load(os.path.join(model_dir, "fuel_model.pkl"))
            self.feature_selector = joblib.load(
                os.path.join(model_dir, "feature_selector.pkl")
            )
            self.scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))
            self.model_metadata = joblib.load(os.path.join(model_dir, "metadata.pkl"))

            logger.info(f"Models loaded from {model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False


class AdvancedEnsembleEngine:
    """Advanced ensemble learning engine with uncertainty quantification"""

    def __init__(self):
        self.base_models = {}
        self.meta_model = None
        self.uncertainty_models = {}
        self.feature_importance = {}
        self.scaler = RobustScaler()
        self.feature_selector = None
        self.model_metadata = {}

    def create_advanced_ensemble(self) -> dict[str, Any]:
        """Create advanced ensemble with diverse base learners"""

        # Diverse base models for ensemble
        base_models = {
            "xgboost": xgb.XGBRegressor(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
            ),
            "extra_trees": ExtraTreesRegressor(
                n_estimators=150, max_depth=12, min_samples_split=5, random_state=42
            ),
            "random_forest": RandomForestRegressor(
                n_estimators=200, max_depth=10, min_samples_split=5, random_state=42
            ),
            "gradient_boost": GradientBoostingRegressor(
                n_estimators=150, learning_rate=0.1, max_depth=8, random_state=42
            ),
            "ada_boost": AdaBoostRegressor(
                n_estimators=100, learning_rate=1.0, random_state=42
            ),
            "elastic_net": ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42),
            "huber": HuberRegressor(epsilon=1.35, max_iter=100),
            "svr": SVR(kernel="rbf", C=1.0, gamma="scale"),
        }

        return base_models

    def train_ensemble_with_uncertainty(
        self, X: np.ndarray, y: np.ndarray
    ) -> dict[str, Any]:
        """Train ensemble models with uncertainty quantification"""

        # Create and train base models
        self.base_models = self.create_advanced_ensemble()
        trained_models = {}
        predictions = []

        # Time series split for temporal data
        tscv = TimeSeriesSplit(n_splits=5)

        for name, model in self.base_models.items():
            try:
                # Cross-validation with time series split
                cv_scores = cross_validate(
                    model,
                    X,
                    y,
                    cv=tscv,
                    scoring=["neg_mean_squared_error", "r2"],
                    return_train_score=True,
                )

                # Train on full dataset
                model.fit(X, y)
                trained_models[name] = {
                    "model": model,
                    "cv_rmse": np.sqrt(
                        -cv_scores["test_neg_mean_squared_error"]
                    ).mean(),
                    "cv_r2": cv_scores["test_r2"].mean(),
                    "predictions": model.predict(X),
                }

                predictions.append(model.predict(X))

                # Feature importance for tree-based models
                if hasattr(model, "feature_importances_"):
                    self.feature_importance[name] = model.feature_importances_

                logger.info(
                    f"Trained {name}: CV RMSE = {trained_models[name]['cv_rmse']:.3f}, CV R² = {trained_models[name]['cv_r2']:.3f}"
                )

            except Exception as e:
                logger.warning(f"Failed to train {name}: {str(e)}")
                continue

        # Train meta-learner (stacking)
        if len(predictions) >= 3:
            meta_features = np.column_stack(predictions)
            self.meta_model = ElasticNet(alpha=0.1, random_state=42)
            self.meta_model.fit(meta_features, y)

            # Ensemble predictions
            ensemble_pred = self.meta_model.predict(meta_features)
            ensemble_rmse = np.sqrt(mean_squared_error(y, ensemble_pred))
            ensemble_r2 = r2_score(y, ensemble_pred)

            logger.info(
                f"Ensemble model: RMSE = {ensemble_rmse:.3f}, R² = {ensemble_r2:.3f}"
            )

        # Train uncertainty models
        self._train_uncertainty_models(X, y, predictions)

        self.model_metadata = {
            "models_trained": list(trained_models.keys()),
            "ensemble_available": self.meta_model is not None,
            "training_samples": len(X),
            "features": X.shape[1],
            "training_timestamp": datetime.now().isoformat(),
        }

        return {
            "trained_models": trained_models,
            "ensemble_performance": {
                "rmse": ensemble_rmse if "ensemble_rmse" in locals() else None,
                "r2": ensemble_r2 if "ensemble_r2" in locals() else None,
            },
            "metadata": self.model_metadata,
        }

    def _train_uncertainty_models(
        self, X: np.ndarray, y: np.ndarray, predictions: list[np.ndarray]
    ):
        """Train models for uncertainty quantification"""

        if len(predictions) < 2:
            return

        # Calculate prediction variance (epistemic uncertainty)
        pred_array = np.array(predictions)
        pred_variance = np.var(pred_array, axis=0)

        # Train model to predict uncertainty
        self.uncertainty_models["variance"] = RandomForestRegressor(
            n_estimators=100, random_state=42
        )
        self.uncertainty_models["variance"].fit(X, pred_variance)

        # Calculate residuals for aleatoric uncertainty
        ensemble_mean = np.mean(pred_array, axis=0)
        residuals = np.abs(y - ensemble_mean)

        self.uncertainty_models["residuals"] = RandomForestRegressor(
            n_estimators=100, random_state=42
        )
        self.uncertainty_models["residuals"].fit(X, residuals)

    def predict_with_uncertainty(self, X: np.ndarray) -> dict[str, Any]:
        """Make predictions with comprehensive uncertainty quantification"""

        if not self.base_models:
            raise ValueError(
                "Models not trained. Call train_ensemble_with_uncertainty first."
            )

        # Get predictions from all base models
        base_predictions = []
        for name, model_info in self.base_models.items():
            if "model" in model_info:
                try:
                    pred = model_info["model"].predict(X)
                    base_predictions.append(pred)
                except Exception as e:
                    logger.warning(f"Prediction failed for {name}: {str(e)}")
                    continue

        if not base_predictions:
            raise ValueError("No models available for prediction")

        base_array = np.array(base_predictions)

        # Ensemble prediction
        if self.meta_model is not None and len(base_predictions) >= 3:
            meta_features = base_array.T
            ensemble_pred = self.meta_model.predict(meta_features)
        else:
            ensemble_pred = np.mean(base_array, axis=0)

        # Uncertainty quantification
        epistemic_uncertainty = np.std(base_array, axis=0)

        # Predict aleatoric uncertainty if models available
        aleatoric_uncertainty = np.zeros_like(ensemble_pred)
        if "residuals" in self.uncertainty_models:
            try:
                aleatoric_uncertainty = self.uncertainty_models["residuals"].predict(X)
            except Exception as e:
                logger.warning(f"Aleatoric uncertainty prediction failed: {str(e)}")

        # Total uncertainty
        total_uncertainty = np.sqrt(epistemic_uncertainty**2 + aleatoric_uncertainty**2)

        # Confidence intervals
        confidence_intervals = {}
        for confidence in [0.68, 0.95, 0.99]:
            z_score = stats.norm.ppf((1 + confidence) / 2)
            lower = ensemble_pred - z_score * total_uncertainty
            upper = ensemble_pred + z_score * total_uncertainty
            confidence_intervals[f"{int(confidence*100)}%"] = (lower, upper)

        # Model confidence (inverse of uncertainty)
        model_confidence = 1.0 / (1.0 + total_uncertainty)

        return {
            "predictions": ensemble_pred,
            "epistemic_uncertainty": epistemic_uncertainty,
            "aleatoric_uncertainty": aleatoric_uncertainty,
            "total_uncertainty": total_uncertainty,
            "confidence_intervals": confidence_intervals,
            "model_confidence": model_confidence,
            "base_predictions": base_array,
            "model_agreement": 1.0
            - (epistemic_uncertainty / (np.abs(ensemble_pred) + 1e-8)),
        }

    def explain_prediction(
        self, X: np.ndarray, feature_names: list[str]
    ) -> dict[str, Any]:
        """Provide model explainability for predictions"""

        explanation = {
            "feature_importance": {},
            "model_contributions": {},
            "uncertainty_sources": {},
        }

        # Aggregate feature importance
        if self.feature_importance:
            avg_importance = np.zeros(len(feature_names))
            for model_name, importance in self.feature_importance.items():
                if len(importance) == len(feature_names):
                    avg_importance += importance

            avg_importance /= len(self.feature_importance)
            explanation["feature_importance"] = dict(zip(feature_names, avg_importance))

        # Model contributions
        for name, model_info in self.base_models.items():
            if "model" in model_info:
                try:
                    pred = model_info["model"].predict(X)
                    explanation["model_contributions"][name] = (
                        pred[0] if len(pred) > 0 else 0
                    )
                except Exception:
                    continue

        # Uncertainty sources
        if "variance" in self.uncertainty_models:
            try:
                pred_variance = self.uncertainty_models["variance"].predict(X)
                explanation["uncertainty_sources"]["prediction_variance"] = (
                    pred_variance[0] if len(pred_variance) > 0 else 0
                )
            except Exception:
                pass

        return explanation


# Singleton instance
analytics_engine = AdvancedAnalytics()

# Initialize the ensemble engine after class definition
analytics_engine.ensemble_engine = AdvancedEnsembleEngine()


def get_analytics_engine() -> AdvancedAnalytics:
    """Get the global analytics engine instance"""
    return analytics_engine
