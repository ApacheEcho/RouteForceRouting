"""
Machine Learning Route Predictor
Uses historical route data to predict optimal routes and select best algorithms
"""
import numpy as np
import pickle
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score
import os

logger = logging.getLogger(__name__)

@dataclass
class MLConfig:
    """Configuration for ML route predictor"""
    model_type: str = 'random_forest'  # 'random_forest', 'gradient_boosting', 'neural_network'
    n_estimators: int = 100
    max_depth: int = 10
    random_state: int = 42
    test_size: float = 0.2
    feature_importance_threshold: float = 0.01
    retrain_interval_days: int = 7
    min_training_samples: int = 50

@dataclass
class RouteFeatures:
    """Features extracted from route data for ML training"""
    num_stores: int = 0
    total_distance: float = 0.0
    avg_distance_between_stores: float = 0.0
    geographic_spread: float = 0.0  # Standard deviation of coordinates
    priority_score: float = 0.0
    demand_total: int = 0
    demand_variance: float = 0.0
    time_of_day: int = 0  # Hour of day (0-23)
    day_of_week: int = 0  # 0=Monday, 6=Sunday
    weather_factor: float = 1.0  # Weather impact factor
    traffic_factor: float = 1.0  # Traffic density factor
    
class MLRoutePredictor:
    """
    Machine Learning-based route predictor and optimizer
    
    Learns from historical route data to:
    1. Predict optimal routes for new scenarios
    2. Select best algorithm for given conditions
    3. Estimate route performance before optimization
    4. Provide intelligent recommendations
    """
    
    def __init__(self, config: MLConfig):
        """
        Initialize ML route predictor
        
        Args:
            config: ML configuration object
        """
        self.config = config
        self.route_predictor = None
        self.algorithm_selector = None
        self.feature_scaler = StandardScaler()
        self.algorithm_encoder = LabelEncoder()
        self.training_data = []
        self.model_path = 'models/ml_route_predictor.pkl'
        self.last_trained = None
        
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        
        # Load existing model if available
        self._load_model()
        
        logger.info(f"Initialized ML Route Predictor with {config.model_type} model")
    
    def _initialize_models(self):
        """Initialize ML models based on configuration"""
        if self.config.model_type == 'random_forest':
            self.route_predictor = RandomForestRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                random_state=self.config.random_state
            )
            self.algorithm_selector = RandomForestRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                random_state=self.config.random_state
            )
        elif self.config.model_type == 'gradient_boosting':
            self.route_predictor = GradientBoostingClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                random_state=self.config.random_state
            )
            self.algorithm_selector = GradientBoostingClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                random_state=self.config.random_state
            )
    
    def extract_features(self, stores: List[Dict[str, Any]], 
                        route_result: Optional[Dict[str, Any]] = None,
                        context: Optional[Dict[str, Any]] = None) -> RouteFeatures:
        """
        Extract features from store data and route context
        
        Args:
            stores: List of store dictionaries
            route_result: Optional route optimization result
            context: Optional context (time, weather, etc.)
            
        Returns:
            RouteFeatures object with extracted features
        """
        features = RouteFeatures()
        
        # AUTO-PILOT: Enhanced input validation and error handling
        try:
            if not stores or not isinstance(stores, list):
                logger.warning("Invalid or empty stores data provided")
                return features
            
            # Basic route features
            features.num_stores = len(stores)
            
            # Geographic features with error handling
            lats = []
            lons = []
            
            for i, store in enumerate(stores):
                try:
                    lat = store.get('lat', store.get('latitude'))
                    lon = store.get('lon', store.get('longitude'))
                    
                    # Validate coordinates
                    if lat is not None and lon is not None:
                        lat_float = float(lat)
                        lon_float = float(lon)
                        
                        # Check if coordinates are within valid range
                        if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                            lats.append(lat_float)
                            lons.append(lon_float)
                        else:
                            logger.warning(f"Invalid coordinates for store {i}: lat={lat}, lon={lon}")
                    else:
                        logger.warning(f"Missing coordinates for store {i}")
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing coordinates for store {i}: {e}")
                    continue
            
            # Calculate geographic spread safely
            if len(lats) >= 2 and len(lons) >= 2:
                try:
                    features.geographic_spread = np.std(lats) + np.std(lons)
                except Exception as e:
                    logger.error(f"Error calculating geographic spread: {e}")
                    features.geographic_spread = 0.0
            
            # Distance calculations with error handling
            distances = []
            for i in range(len(lats)):
                for j in range(i + 1, len(lats)):
                    try:
                        dist = self._calculate_distance(lats[i], lons[i], lats[j], lons[j])
                        if dist is not None and dist > 0:
                            distances.append(dist)
                    except Exception as e:
                        logger.warning(f"Error calculating distance between stores {i} and {j}: {e}")
                        continue
            
            # Calculate distance-based features safely
            if distances:
                try:
                    features.total_distance = sum(distances)
                    features.avg_distance_between_stores = np.mean(distances)
                except Exception as e:
                    logger.error(f"Error calculating distance features: {e}")
                    features.total_distance = 0.0
                    features.avg_distance_between_stores = 0.0
            
            # Priority and demand features with error handling
            try:
                priorities = []
                demands = []
                
                for store in stores:
                    try:
                        priority = float(store.get('priority', 1))
                        demand = float(store.get('demand', 0))
                        priorities.append(priority)
                        demands.append(demand)
                    except (ValueError, TypeError):
                        priorities.append(1.0)  # Default priority
                        demands.append(0.0)    # Default demand
                
                features.priority_score = sum(p * (len(stores) - i) for i, p in enumerate(priorities))
                features.demand_total = sum(demands)
                features.demand_variance = np.var(demands) if demands else 0.0
                
            except Exception as e:
                logger.error(f"Error calculating priority/demand features: {e}")
                features.priority_score = len(stores)  # Default
                features.demand_total = 0.0
                features.demand_variance = 0.0
            
            # Temporal features with error handling
            try:
                if context and isinstance(context, dict):
                    timestamp = context.get('timestamp')
                    if timestamp:
                        if isinstance(timestamp, datetime):
                            now = timestamp
                        else:
                            now = datetime.fromisoformat(str(timestamp))
                    else:
                        now = datetime.now()
                    
                    features.time_of_day = now.hour
                    features.day_of_week = now.weekday()
                    
                    # Weather and traffic factors
                    features.weather_factor = float(context.get('weather_factor', 1.0))
                    features.traffic_factor = float(context.get('traffic_factor', 1.0))
                    
            except Exception as e:
                logger.warning(f"Error extracting temporal features: {e}")
                now = datetime.now()
                features.time_of_day = now.hour
                features.day_of_week = now.weekday()
                features.weather_factor = 1.0
                features.traffic_factor = 1.0
                
        except Exception as e:
            logger.error(f"Critical error in feature extraction: {e}")
            # Return default features if everything fails
            features = RouteFeatures()
            features.num_stores = len(stores) if stores else 0
            features.weather_factor = context.get('weather_factor', 1.0)
            features.traffic_factor = context.get('traffic_factor', 1.0)
        else:
            now = datetime.now()
            features.time_of_day = now.hour
            features.day_of_week = now.weekday()
        
        return features
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate Haversine distance between two points"""
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return c * 6371  # Earth's radius in km
    
    def add_training_data(self, stores: List[Dict[str, Any]], 
                         algorithm_used: str, 
                         performance_metrics: Dict[str, Any],
                         context: Optional[Dict[str, Any]] = None):
        """
        Add training data from route optimization results
        
        Args:
            stores: Store data used for optimization
            algorithm_used: Algorithm that was used
            performance_metrics: Performance metrics from optimization
            context: Optional context information
        """
        features = self.extract_features(stores, performance_metrics, context)
        
        training_sample = {
            'features': features,
            'algorithm': algorithm_used,
            'performance': performance_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        self.training_data.append(training_sample)
        
        # Auto-retrain if we have enough data
        if len(self.training_data) >= self.config.min_training_samples:
            if (self.last_trained is None or 
                datetime.now() - self.last_trained > timedelta(days=self.config.retrain_interval_days)):
                self.train_models()
    
    def train_models(self) -> Dict[str, float]:
        """
        Train ML models on collected data
        
        Returns:
            Dictionary with training metrics
        """
        if len(self.training_data) < self.config.min_training_samples:
            logger.warning(f"Not enough training data: {len(self.training_data)} < {self.config.min_training_samples}")
            return {}
        
        logger.info(f"Training ML models with {len(self.training_data)} samples")
        
        # Prepare training data
        X = []
        y_performance = []
        y_algorithm = []
        
        for sample in self.training_data:
            features = sample['features']
            feature_vector = [
                features.num_stores,
                features.total_distance,
                features.avg_distance_between_stores,
                features.geographic_spread,
                features.priority_score,
                features.demand_total,
                features.demand_variance,
                features.time_of_day,
                features.day_of_week,
                features.weather_factor,
                features.traffic_factor
            ]
            
            X.append(feature_vector)
            y_performance.append(sample['performance'].get('improvement_percent', 0))
            y_algorithm.append(sample['algorithm'])
        
        X = np.array(X)
        y_performance = np.array(y_performance)
        
        # Scale features
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Encode algorithms
        y_algorithm_encoded = self.algorithm_encoder.fit_transform(y_algorithm)
        
        # Split data
        X_train, X_test, y_perf_train, y_perf_test = train_test_split(
            X_scaled, y_performance, test_size=self.config.test_size, random_state=self.config.random_state
        )
        
        X_train_algo, X_test_algo, y_algo_train, y_algo_test = train_test_split(
            X_scaled, y_algorithm_encoded, test_size=self.config.test_size, random_state=self.config.random_state
        )
        
        # Train route performance predictor
        self.route_predictor.fit(X_train, y_perf_train)
        y_perf_pred = self.route_predictor.predict(X_test)
        perf_mse = mean_squared_error(y_perf_test, y_perf_pred)
        
        # Train algorithm selector
        self.algorithm_selector.fit(X_train_algo, y_algo_train)
        y_algo_pred = self.algorithm_selector.predict(X_test_algo)
        algo_accuracy = accuracy_score(y_algo_test, y_algo_pred)
        
        # Update training timestamp
        self.last_trained = datetime.now()
        
        # Save model
        self._save_model()
        
        metrics = {
            'performance_mse': perf_mse,
            'algorithm_accuracy': algo_accuracy,
            'training_samples': len(self.training_data),
            'trained_at': self.last_trained.isoformat()
        }
        
        logger.info(f"Model training completed - Performance MSE: {perf_mse:.4f}, Algorithm Accuracy: {algo_accuracy:.4f}")
        
        return metrics
    
    def predict_route_performance(self, stores: List[Dict[str, Any]], 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Predict route optimization performance for given stores
        
        Args:
            stores: Store data for prediction
            context: Optional context information
            
        Returns:
            Dictionary with performance predictions
        """
        if self.route_predictor is None:
            return {'predicted_improvement': 0.0, 'confidence': 0.0}
        
        features = self.extract_features(stores, context=context)
        feature_vector = np.array([[
            features.num_stores,
            features.total_distance,
            features.avg_distance_between_stores,
            features.geographic_spread,
            features.priority_score,
            features.demand_total,
            features.demand_variance,
            features.time_of_day,
            features.day_of_week,
            features.weather_factor,
            features.traffic_factor
        ]])
        
        try:
            feature_vector_scaled = self.feature_scaler.transform(feature_vector)
            prediction = self.route_predictor.predict(feature_vector_scaled)[0]
            
            # Calculate confidence based on feature importance
            if hasattr(self.route_predictor, 'feature_importances_'):
                confidence = np.mean(self.route_predictor.feature_importances_)
            else:
                confidence = 0.5
            
            return {
                'predicted_improvement': float(prediction),
                'confidence': float(confidence),
                'num_stores': features.num_stores,
                'complexity_score': features.geographic_spread + features.demand_variance
            }
            
        except Exception as e:
            logger.error(f"Error predicting route performance: {str(e)}")
            return {'predicted_improvement': 0.0, 'confidence': 0.0}
    
    def recommend_algorithm(self, stores: List[Dict[str, Any]], 
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recommend best algorithm for given stores and context
        
        Args:
            stores: Store data for recommendation
            context: Optional context information
            
        Returns:
            Dictionary with algorithm recommendation
        """
        if self.algorithm_selector is None:
            return {
                'recommended_algorithm': 'genetic',
                'confidence': 0.0,
                'reasoning': 'Default recommendation - no trained model available'
            }
        
        features = self.extract_features(stores, context=context)
        feature_vector = np.array([[
            features.num_stores,
            features.total_distance,
            features.avg_distance_between_stores,
            features.geographic_spread,
            features.priority_score,
            features.demand_total,
            features.demand_variance,
            features.time_of_day,
            features.day_of_week,
            features.weather_factor,
            features.traffic_factor
        ]])
        
        try:
            feature_vector_scaled = self.feature_scaler.transform(feature_vector)
            prediction = self.algorithm_selector.predict(feature_vector_scaled)[0]
            
            # Get algorithm name
            algorithm_name = self.algorithm_encoder.inverse_transform([prediction])[0]
            
            # Calculate confidence
            if hasattr(self.algorithm_selector, 'predict_proba'):
                probabilities = self.algorithm_selector.predict_proba(feature_vector_scaled)[0]
                confidence = np.max(probabilities)
            else:
                confidence = 0.7  # Default confidence for regression models
            
            # Generate reasoning
            reasoning = self._generate_reasoning(features, algorithm_name)
            
            return {
                'recommended_algorithm': algorithm_name,
                'confidence': float(confidence),
                'reasoning': reasoning,
                'features_used': {
                    'num_stores': features.num_stores,
                    'geographic_spread': features.geographic_spread,
                    'complexity': features.demand_variance
                }
            }
            
        except Exception as e:
            logger.error(f"Error recommending algorithm: {str(e)}")
            return {
                'recommended_algorithm': 'genetic',
                'confidence': 0.0,
                'reasoning': f'Error in recommendation: {str(e)}'
            }
    
    def _generate_reasoning(self, features: RouteFeatures, algorithm: str) -> str:
        """Generate human-readable reasoning for algorithm recommendation"""
        if algorithm == 'genetic':
            if features.num_stores > 15:
                return "Genetic algorithm recommended for large number of stores (>15) - excels at complex optimization"
            else:
                return "Genetic algorithm recommended for balanced performance across different scenarios"
        elif algorithm == 'simulated_annealing':
            if features.geographic_spread > 0.1:
                return "Simulated annealing recommended for geographically dispersed stores - good at escaping local optima"
            else:
                return "Simulated annealing recommended for quick optimization with good results"
        elif algorithm == 'multi_objective':
            return "Multi-objective optimization recommended for complex scenarios with multiple competing objectives"
        else:
            return f"Algorithm {algorithm} recommended based on historical performance patterns"
    
    def _save_model(self):
        """Save trained model to disk"""
        try:
            model_data = {
                'route_predictor': self.route_predictor,
                'algorithm_selector': self.algorithm_selector,
                'feature_scaler': self.feature_scaler,
                'algorithm_encoder': self.algorithm_encoder,
                'training_data': self.training_data[-1000:],  # Keep last 1000 samples
                'last_trained': self.last_trained.isoformat() if self.last_trained else None,
                'config': self.config
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def _load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.route_predictor = model_data.get('route_predictor')
                self.algorithm_selector = model_data.get('algorithm_selector')
                self.feature_scaler = model_data.get('feature_scaler', StandardScaler())
                self.algorithm_encoder = model_data.get('algorithm_encoder', LabelEncoder())
                self.training_data = model_data.get('training_data', [])
                
                last_trained_str = model_data.get('last_trained')
                if last_trained_str:
                    self.last_trained = datetime.fromisoformat(last_trained_str)
                
                logger.info(f"Model loaded from {self.model_path}")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model"""
        return {
            'model_type': self.config.model_type,
            'training_samples': len(self.training_data),
            'last_trained': self.last_trained.isoformat() if self.last_trained else None,
            'is_trained': self.route_predictor is not None,
            'model_path': self.model_path
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained models"""
        if self.route_predictor is None or not hasattr(self.route_predictor, 'feature_importances_'):
            return {}
        
        feature_names = [
            'num_stores', 'total_distance', 'avg_distance_between_stores',
            'geographic_spread', 'priority_score', 'demand_total',
            'demand_variance', 'time_of_day', 'day_of_week',
            'weather_factor', 'traffic_factor'
        ]
        
        importances = self.route_predictor.feature_importances_
        
        return dict(zip(feature_names, importances))
