"""
Comprehensive tests for Core Route Optimization Algorithm
Tests the CoreRouteOptimizer class with various scenarios and edge cases.
"""

import math
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

# Set up the Python path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core_optimizer import (
    CoreRouteOptimizer,
    OptimizationConfig,
    OptimizationObjective,
    CostFactors,
    OptimizationResult
)
from routing_engine import Store, Vehicle, VehicleStatus, OptimizationMethod


class TestCoreRouteOptimizer:
    """Test suite for CoreRouteOptimizer class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.optimizer = CoreRouteOptimizer()
        self.sample_stores = self.create_sample_stores()
        self.sample_vehicles = self.create_sample_vehicles()
    
    def create_sample_stores(self) -> list:
        """Create sample stores for testing."""
        return [
            Store(
                store_id="STORE_001",
                name="Downtown Market",
                address="123 Main St",
                coordinates={"lat": 40.7128, "lng": -74.0060},
                delivery_window="09:00-17:00",
                priority="high",
                estimated_service_time=15,
                packages=5,
                weight_kg=25.0
            ),
            Store(
                store_id="STORE_002", 
                name="Uptown Shop",
                address="456 Broadway",
                coordinates={"lat": 40.7831, "lng": -73.9712},
                delivery_window="10:00-18:00",
                priority="medium",
                estimated_service_time=20,
                packages=8,
                weight_kg=40.0
            ),
            Store(
                store_id="STORE_003",
                name="Suburban Store",
                address="789 Park Ave",
                coordinates={"lat": 40.6892, "lng": -74.0445},
                delivery_window="08:00-16:00",
                priority="low",
                estimated_service_time=10,
                packages=3,
                weight_kg=15.0
            )
        ]
    
    def create_sample_vehicles(self) -> list:
        """Create sample vehicles for testing."""
        return [
            Vehicle(
                vehicle_id="VAN_001",
                capacity_kg=500.0,
                max_packages=50,
                max_driving_hours=8.0,
                status=VehicleStatus.AVAILABLE,
                driver_id="DRIVER_001"
            ),
            Vehicle(
                vehicle_id="TRUCK_001",
                capacity_kg=1000.0,
                max_packages=100,
                max_driving_hours=10.0,
                status=VehicleStatus.AVAILABLE,
                driver_id="DRIVER_002"
            )
        ]
    
    def test_optimizer_initialization(self):
        """Test CoreRouteOptimizer initialization."""
        # Test default initialization
        optimizer = CoreRouteOptimizer()
        assert optimizer.config is not None
        assert optimizer.config.objective == OptimizationObjective.BALANCED
        assert optimizer.base_optimizer is not None
        assert optimizer.optimization_history == []
        
        # Test custom configuration
        custom_config = OptimizationConfig(
            objective=OptimizationObjective.MINIMIZE_COST,
            time_limit_seconds=60.0
        )
        optimizer = CoreRouteOptimizer(custom_config)
        assert optimizer.config.objective == OptimizationObjective.MINIMIZE_COST
        assert optimizer.config.time_limit_seconds == 60.0
    
    def test_cost_factors_configuration(self):
        """Test CostFactors configuration."""
        cost_factors = CostFactors(
            fuel_cost_per_km=0.20,
            driver_hourly_rate=30.0,
            vehicle_depreciation_per_km=0.08
        )
        
        config = OptimizationConfig(cost_factors=cost_factors)
        optimizer = CoreRouteOptimizer(config)
        
        assert optimizer.config.cost_factors.fuel_cost_per_km == 0.20
        assert optimizer.config.cost_factors.driver_hourly_rate == 30.0
        assert optimizer.config.cost_factors.vehicle_depreciation_per_km == 0.08
    
    def test_problem_characteristics_analysis(self):
        """Test problem characteristics analysis."""
        profile = self.optimizer._analyze_problem_characteristics(
            self.sample_stores, self.sample_vehicles
        )
        
        assert 'num_stores' in profile
        assert 'num_vehicles' in profile
        assert 'geographical_spread' in profile
        assert 'capacity_utilization' in profile
        assert 'priority_complexity' in profile
        assert 'problem_size_category' in profile
        assert 'constraint_complexity' in profile
        
        assert profile['num_stores'] == 3
        assert profile['num_vehicles'] == 2
        assert profile['problem_size_category'] == 'small'
        assert 0 <= profile['capacity_utilization'] <= 1
        assert 0 <= profile['priority_complexity'] <= 1
    
    def test_algorithm_selection(self):
        """Test algorithm selection logic."""
        # Small problem should use TWO_OPT
        small_profile = {
            'num_stores': 5,
            'geographical_spread': 0.1,
            'capacity_utilization': 0.5,
            'priority_complexity': 0.2
        }
        method = self.optimizer._select_optimization_algorithm(small_profile)
        assert method == OptimizationMethod.TWO_OPT
        
        # Medium problem with high complexity should use GENETIC_ALGORITHM
        medium_complex_profile = {
            'num_stores': 25,
            'geographical_spread': 0.5,
            'capacity_utilization': 0.9,
            'priority_complexity': 0.4
        }
        method = self.optimizer._select_optimization_algorithm(medium_complex_profile)
        assert method == OptimizationMethod.GENETIC_ALGORITHM
        
        # Large geographically dispersed problem should use SIMULATED_ANNEALING
        large_dispersed_profile = {
            'num_stores': 100,
            'geographical_spread': 1.5,
            'capacity_utilization': 0.6,
            'priority_complexity': 0.3
        }
        method = self.optimizer._select_optimization_algorithm(large_dispersed_profile)
        assert method == OptimizationMethod.SIMULATED_ANNEALING
        
        # Very large problem should use NEAREST_NEIGHBOR
        very_large_profile = {
            'num_stores': 300,
            'geographical_spread': 0.8,
            'capacity_utilization': 0.7,
            'priority_complexity': 0.2
        }
        method = self.optimizer._select_optimization_algorithm(very_large_profile)
        assert method == OptimizationMethod.NEAREST_NEIGHBOR
    
    def test_store_preprocessing(self):
        """Test store preprocessing and filtering."""
        # Test without constraints
        filtered = self.optimizer._preprocess_stores(self.sample_stores, {})
        assert len(filtered) == 3
        
        # Test with priority filtering
        constraints = {'min_priority': 'medium'}
        filtered = self.optimizer._preprocess_stores(self.sample_stores, constraints)
        # Should include high and medium priority stores
        assert len(filtered) == 2
        
        # Test with geographical filtering
        constraints = {
            'max_radius_km': 50.0,
            'depot_location': {'lat': 40.7128, 'lng': -74.0060}
        }
        filtered = self.optimizer._preprocess_stores(self.sample_stores, constraints)
        assert len(filtered) <= 3  # All should be within reasonable distance
    
    def test_vehicle_filtering(self):
        """Test vehicle availability filtering."""
        # Add unavailable vehicle
        vehicles = self.sample_vehicles.copy()
        vehicles.append(Vehicle(
            vehicle_id="VAN_002",
            capacity_kg=500.0,
            max_packages=50,
            max_driving_hours=8.0,
            status=VehicleStatus.MAINTENANCE,
            driver_id="DRIVER_003"
        ))
        
        available = self.optimizer._filter_available_vehicles(vehicles)
        assert len(available) == 2  # Only available vehicles
        assert all(v.status == VehicleStatus.AVAILABLE for v in available)
    
    def test_route_cost_calculation(self):
        """Test comprehensive route cost calculation."""
        cost = self.optimizer._calculate_route_cost(self.sample_stores)
        
        assert cost > 0
        assert isinstance(cost, float)
        
        # Cost should increase with more stores
        single_store_cost = self.optimizer._calculate_route_cost([self.sample_stores[0]])
        assert cost > single_store_cost
        
        # Empty route should have zero cost
        empty_cost = self.optimizer._calculate_route_cost([])
        assert empty_cost == 0.0
    
    def test_efficiency_score_calculation(self):
        """Test efficiency score calculation."""
        # Create mock routes
        from routing_engine import Route
        routes = [
            Route(
                route_id="ROUTE_001",
                vehicle_id="VAN_001",
                driver_id="DRIVER_001",
                stops=[
                    {"store_id": "STORE_001", "sequence": 1},
                    {"store_id": "STORE_002", "sequence": 2}
                ],
                total_distance_km=15.0,
                estimated_duration_hours=2.0,
                total_weight_kg=65.0,
                total_packages=13,
                optimization_method="test",
                created_at=datetime.now()
            )
        ]
        
        efficiency = self.optimizer._calculate_efficiency_score(routes, self.sample_stores)
        
        assert 0.0 <= efficiency <= 100.0
        assert isinstance(efficiency, float)
        
        # Empty routes should return 0 efficiency
        empty_efficiency = self.optimizer._calculate_efficiency_score([], self.sample_stores)
        assert empty_efficiency == 0.0
    
    def test_comprehensive_cost_breakdown(self):
        """Test comprehensive cost breakdown calculation."""
        from routing_engine import Route
        routes = [
            Route(
                route_id="ROUTE_001",
                vehicle_id="VAN_001",
                driver_id="DRIVER_001",
                stops=[{"store_id": "STORE_001", "sequence": 1}],
                total_distance_km=20.0,
                estimated_duration_hours=3.0,
                total_weight_kg=25.0,
                total_packages=5,
                optimization_method="test",
                created_at=datetime.now()
            )
        ]
        
        costs = self.optimizer._calculate_comprehensive_costs(routes)
        
        required_keys = ['fuel_cost', 'driver_cost', 'vehicle_depreciation', 'time_penalties', 'priority_penalties']
        for key in required_keys:
            assert key in costs
            assert costs[key] >= 0
            assert isinstance(costs[key], float)
        
        # Fuel cost should be distance * fuel_rate
        expected_fuel_cost = 20.0 * self.optimizer.config.cost_factors.fuel_cost_per_km
        assert costs['fuel_cost'] == expected_fuel_cost
        
        # Driver cost should be time * hourly_rate
        expected_driver_cost = 3.0 * self.optimizer.config.cost_factors.driver_hourly_rate
        assert costs['driver_cost'] == expected_driver_cost
    
    def test_optimization_statistics(self):
        """Test optimization statistics tracking."""
        # Initially should be empty
        stats = self.optimizer.get_optimization_statistics()
        assert 'message' in stats or 'total_optimizations' in stats
        
        # Add some mock history
        self.optimizer.optimization_history = [
            {
                'timestamp': datetime.now(),
                'problem_size': 10,
                'method_used': 'nearest_neighbor',
                'processing_time': 1.5,
                'efficiency_score': 85.0,
                'total_cost': 150.0
            },
            {
                'timestamp': datetime.now(),
                'problem_size': 20,
                'method_used': 'genetic_algorithm',
                'processing_time': 5.2,
                'efficiency_score': 92.0,
                'total_cost': 280.0
            }
        ]
        
        stats = self.optimizer.get_optimization_statistics()
        
        assert stats['total_optimizations'] == 2
        assert stats['avg_processing_time'] == (1.5 + 5.2) / 2
        assert stats['avg_efficiency_score'] == (85.0 + 92.0) / 2
        assert 'algorithm_usage' in stats
        assert 'problem_size_distribution' in stats
    
    def test_problem_size_categorization(self):
        """Test problem size categorization."""
        assert self.optimizer._categorize_problem_size(5) == 'small'
        assert self.optimizer._categorize_problem_size(25) == 'medium'
        assert self.optimizer._categorize_problem_size(100) == 'large'
        assert self.optimizer._categorize_problem_size(500) == 'extra_large'
    
    def test_constraint_complexity_assessment(self):
        """Test constraint complexity assessment."""
        complexity = self.optimizer._assess_constraint_complexity(
            self.sample_stores, self.sample_vehicles
        )
        
        assert 0.0 <= complexity <= 1.0
        assert isinstance(complexity, float)
        
        # Empty lists should return 0 complexity
        empty_complexity = self.optimizer._assess_constraint_complexity([], [])
        assert empty_complexity >= 0.0
    
    def test_full_optimization_workflow(self):
        """Test the complete optimization workflow."""
        result = self.optimizer.optimize_routes(
            self.sample_stores,
            self.sample_vehicles
        )
        
        # Verify result structure
        assert isinstance(result, OptimizationResult)
        assert hasattr(result, 'routes')
        assert hasattr(result, 'total_cost')
        assert hasattr(result, 'total_distance_km')
        assert hasattr(result, 'total_time_hours')
        assert hasattr(result, 'optimization_method_used')
        assert hasattr(result, 'convergence_achieved')
        assert hasattr(result, 'processing_time_seconds')
        assert hasattr(result, 'cost_breakdown')
        assert hasattr(result, 'efficiency_score')
        assert hasattr(result, 'algorithm_performance')
        
        # Verify result values
        assert len(result.routes) > 0
        assert result.total_cost >= 0
        assert result.total_distance_km >= 0
        assert result.total_time_hours >= 0
        assert result.processing_time_seconds >= 0
        assert 0 <= result.efficiency_score <= 100
        
        # Verify cost breakdown
        assert isinstance(result.cost_breakdown, dict)
        assert sum(result.cost_breakdown.values()) == result.total_cost
        
        # Verify optimization history is updated
        assert len(self.optimizer.optimization_history) == 1
    
    def test_optimization_with_constraints(self):
        """Test optimization with various constraints."""
        constraints = {
            'min_priority': 'medium',
            'max_radius_km': 100.0,
            'depot_location': {'lat': 40.7128, 'lng': -74.0060}
        }
        
        result = self.optimizer.optimize_routes(
            self.sample_stores,
            self.sample_vehicles,
            constraints
        )
        
        assert isinstance(result, OptimizationResult)
        assert len(result.routes) > 0
        assert result.total_cost >= 0
    
    def test_optimization_with_no_available_vehicles(self):
        """Test optimization when no vehicles are available."""
        unavailable_vehicles = [
            Vehicle(
                vehicle_id="VAN_001",
                capacity_kg=500.0,
                max_packages=50,
                max_driving_hours=8.0,
                status=VehicleStatus.MAINTENANCE,
                driver_id="DRIVER_001"
            )
        ]
        
        with pytest.raises(ValueError, match="No available vehicles"):
            self.optimizer.optimize_routes(
                self.sample_stores,
                unavailable_vehicles
            )
    
    def test_optimization_with_empty_stores(self):
        """Test optimization with empty store list."""
        result = self.optimizer.optimize_routes(
            [],
            self.sample_vehicles
        )
        
        assert isinstance(result, OptimizationResult)
        assert len(result.routes) == 0
        assert result.total_cost == 0
        assert result.total_distance_km == 0
        assert result.total_time_hours == 0
    
    def test_cost_aware_local_search(self):
        """Test cost-aware local search optimization."""
        # Test with small set of stores
        optimized = self.optimizer._cost_aware_local_search(self.sample_stores[:2])
        assert len(optimized) == 2
        assert all(store in self.sample_stores for store in optimized)
        
        # Test with single store (should return unchanged)
        single_store = self.optimizer._cost_aware_local_search([self.sample_stores[0]])
        assert len(single_store) == 1
        assert single_store[0] == self.sample_stores[0]
        
        # Test with empty list
        empty_result = self.optimizer._cost_aware_local_search([])
        assert len(empty_result) == 0


class TestOptimizationConfig:
    """Test suite for OptimizationConfig class."""
    
    def test_default_initialization(self):
        """Test default configuration initialization."""
        config = OptimizationConfig()
        
        assert config.objective == OptimizationObjective.BALANCED
        assert config.cost_factors is not None
        assert config.time_limit_seconds == 30.0
        assert config.max_iterations == 1000
        assert config.convergence_threshold == 0.001
        assert config.enable_traffic_awareness is True
        assert config.enable_dynamic_pricing is False
    
    def test_custom_initialization(self):
        """Test custom configuration initialization."""
        custom_cost_factors = CostFactors(
            fuel_cost_per_km=0.25,
            driver_hourly_rate=35.0
        )
        
        config = OptimizationConfig(
            objective=OptimizationObjective.MINIMIZE_COST,
            cost_factors=custom_cost_factors,
            time_limit_seconds=60.0,
            max_iterations=2000
        )
        
        assert config.objective == OptimizationObjective.MINIMIZE_COST
        assert config.cost_factors.fuel_cost_per_km == 0.25
        assert config.cost_factors.driver_hourly_rate == 35.0
        assert config.time_limit_seconds == 60.0
        assert config.max_iterations == 2000


class TestCostFactors:
    """Test suite for CostFactors class."""
    
    def test_default_values(self):
        """Test default cost factor values."""
        cost_factors = CostFactors()
        
        assert cost_factors.fuel_cost_per_km == 0.15
        assert cost_factors.driver_hourly_rate == 25.0
        assert cost_factors.vehicle_depreciation_per_km == 0.05
        assert cost_factors.traffic_delay_penalty == 50.0
        assert cost_factors.priority_penalty_multiplier == 2.0
        assert cost_factors.overtime_penalty_rate == 1.5
    
    def test_custom_values(self):
        """Test custom cost factor values."""
        cost_factors = CostFactors(
            fuel_cost_per_km=0.20,
            driver_hourly_rate=30.0,
            vehicle_depreciation_per_km=0.08,
            traffic_delay_penalty=75.0,
            priority_penalty_multiplier=3.0,
            overtime_penalty_rate=2.0
        )
        
        assert cost_factors.fuel_cost_per_km == 0.20
        assert cost_factors.driver_hourly_rate == 30.0
        assert cost_factors.vehicle_depreciation_per_km == 0.08
        assert cost_factors.traffic_delay_penalty == 75.0
        assert cost_factors.priority_penalty_multiplier == 3.0
        assert cost_factors.overtime_penalty_rate == 2.0


if __name__ == "__main__":
    """Run tests directly if script is executed."""
    import pytest
    pytest.main([__file__, "-v"])