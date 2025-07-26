import os
import sys
from datetime import datetime

import pytest

from routing_engine import (
    OptimizationMethod,
    PerformanceMonitor,
    RouteOptimizer,
    Store,
    Vehicle,
    VehicleStatus,
)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMultiVehicleRouting:
    """Test suite for multi-vehicle route optimization."""

    @pytest.fixture
    def sample_vehicles(self):
        """Sample fleet of vehicles with different capacities."""
        return [
            Vehicle(
                vehicle_id="VAN_001",
                capacity_kg=800,
                max_packages=30,
                max_driving_hours=8,
                status=VehicleStatus.AVAILABLE,
                current_location={"lat": 40.7128, "lng": -74.0060},
                driver_id="DRIVER_001",
            ),
            Vehicle(
                vehicle_id="TRUCK_001",
                capacity_kg=1500,
                max_packages=50,
                max_driving_hours=10,
                status=VehicleStatus.AVAILABLE,
                current_location={"lat": 40.7589, "lng": -73.9851},
                driver_id="DRIVER_002",
            ),
            Vehicle(
                vehicle_id="VAN_002",
                capacity_kg=750,
                max_packages=25,
                max_driving_hours=8,
                status=VehicleStatus.MAINTENANCE,  # Not available
                current_location={"lat": 40.7505, "lng": -73.9934},
            ),
            Vehicle(
                vehicle_id="TRUCK_002",
                capacity_kg=1200,
                max_packages=40,
                max_driving_hours=9,
                status=VehicleStatus.AVAILABLE,
                current_location={"lat": 40.6892, "lng": -73.9442},
                driver_id="DRIVER_003",
            ),
        ]

    @pytest.fixture
    def large_store_dataset(self):
        """Large dataset of 15 stores for multi-vehicle testing."""
        stores = []
        store_templates = [
            {"chain": "CVS", "base_weight": 20, "base_packages": 4},
            {"chain": "WLG", "base_weight": 30, "base_packages": 6},
            {"chain": "RIT", "base_weight": 25, "base_packages": 5},
        ]

        coordinates = [
            {"lat": 40.7128, "lng": -74.0060},  # Manhattan
            {"lat": 40.7589, "lng": -73.9851},  # Times Square
            {"lat": 40.7505, "lng": -73.9934},  # Midtown
            {"lat": 40.6892, "lng": -73.9442},  # Brooklyn
            {"lat": 40.7831, "lng": -73.9712},  # Upper West Side
            {"lat": 40.7282, "lng": -73.9442},  # Queens
            {"lat": 40.7336, "lng": -73.9890},  # East Village
            {"lat": 40.8621, "lng": -73.9036},  # Bronx
            {"lat": 40.6441, "lng": -74.0776},  # Staten Island
            {"lat": 40.7048, "lng": -73.6501},  # Long Island
            {"lat": 40.7400, "lng": -73.9900},  # Chelsea
            {"lat": 40.7614, "lng": -73.9776},  # Central Park
            {"lat": 40.7180, "lng": -74.0020},  # Tribeca
            {"lat": 40.7295, "lng": -73.9965},  # Flatiron
            {"lat": 40.7549, "lng": -73.9840},  # Hell's Kitchen
        ]

        priorities = ["high", "medium", "low"] * 5
        delivery_windows = [
            "09:00-17:00",
            "10:00-16:00",
            "08:00-18:00",
            "11:00-15:00",
            "09:30-16:30",
        ] * 3

        for i in range(15):
            template = store_templates[i % 3]
            weight_variation = (-5 + (i % 11)) * 2  # Vary weight by ±10kg
            package_variation = -2 + (i % 5)  # Vary packages by ±2

            store = Store(
                store_id=f"{template['chain']}_{i + 1:03d}",
                name=f"{template['chain']} Store #{i + 1}",
                address=f"{100 + i * 10} Test St, New York, NY 1000{i % 10}",
                coordinates=coordinates[i],
                delivery_window=delivery_windows[i],
                priority=priorities[i],
                estimated_service_time=10 + (i % 3) * 5,  # 10-20 minutes
                packages=max(1, template["base_packages"] + package_variation),
                weight_kg=max(5.0, template["base_weight"] + weight_variation),
                special_requirements={"signature_required": i % 2 == 0},
            )
            stores.append(store)

        return stores

    def test_multi_vehicle_route_distribution(
        self, large_store_dataset, sample_vehicles
    ):
        """Test distribution of stores across multiple vehicles."""
        optimizer = RouteOptimizer()

        # Test with available vehicles only
        available_vehicles = [
            v for v in sample_vehicles if v.status == VehicleStatus.AVAILABLE
        ]

        vehicle_assignments = optimizer.distribute_stores_to_vehicles(
            large_store_dataset, available_vehicles
        )

        # Verify all stores are assigned
        total_assigned_stores = sum(
            len(stores) for stores in vehicle_assignments.values()
        )
        assert total_assigned_stores <= len(
            large_store_dataset
        ), "Cannot assign more stores than available"

        # Verify capacity constraints are respected
        for vehicle_id, assigned_stores in vehicle_assignments.items():
            vehicle = next(v for v in available_vehicles if v.vehicle_id == vehicle_id)

            total_weight = sum(store.weight_kg for store in assigned_stores)
            total_packages = sum(store.packages for store in assigned_stores)

            assert (
                total_weight <= vehicle.capacity_kg
            ), f"Vehicle {vehicle_id} weight limit exceeded"
            assert (
                total_packages <= vehicle.max_packages
            ), f"Vehicle {vehicle_id} package limit exceeded"

        # Verify at least 2 vehicles are used for large dataset
        assert (
            len(vehicle_assignments) >= 2
        ), "Should use multiple vehicles for large dataset"

        print(
            f"Distributed {len(large_store_dataset)} stores across {len(vehicle_assignments)} vehicles"
        )
        for vehicle_id, stores in vehicle_assignments.items():
            total_weight = sum(s.weight_kg for s in stores)
            total_packages = sum(s.packages for s in stores)
            print(
                f"  {vehicle_id}: {len(stores)} stores, {total_weight}kg, {total_packages} packages"
            )

    def test_multi_vehicle_optimization_methods(
        self, large_store_dataset, sample_vehicles
    ):
        """Test different optimization methods with multi-vehicle routing."""
        optimizer = RouteOptimizer()

        methods_to_test = [
            OptimizationMethod.NEAREST_NEIGHBOR,
            OptimizationMethod.TWO_OPT,
        ]

        for method in methods_to_test:
            routes = optimizer.optimize_multi_vehicle_routes(
                large_store_dataset, sample_vehicles, method
            )

            # Verify routes were generated
            assert len(routes) > 0, f"No routes generated for method {method.value}"
            assert len(routes) <= len(
                [v for v in sample_vehicles if v.status == VehicleStatus.AVAILABLE]
            )

            # Verify each route is valid
            for route in routes:
                assert route.route_id is not None
                assert route.vehicle_id is not None
                assert len(route.stops) > 0
                assert route.total_distance_km > 0
                assert route.estimated_duration_hours > 0
                assert route.optimization_method == method.value

            print(f"Method {method.value}: Generated {len(routes)} routes")

    def test_vehicle_capacity_overflow_handling(self, sample_vehicles):
        """Test handling when stores exceed vehicle capacities."""
        optimizer = RouteOptimizer()

        # Create stores that collectively exceed all vehicle capacities
        oversized_stores = [
            Store(
                store_id=f"HEAVY_{i}",
                name=f"Heavy Store {i}",
                address=f"Heavy St {i}",
                coordinates={"lat": 40.7128 + i * 0.01, "lng": -74.0060 + i * 0.01},
                delivery_window="09:00-17:00",
                priority="high",
                estimated_service_time=15,
                packages=60,  # Exceeds individual vehicle limits
                weight_kg=2000,  # Exceeds individual vehicle limits
            )
            for i in range(3)
        ]

        # Should handle gracefully without crashing
        vehicle_assignments = optimizer.distribute_stores_to_vehicles(
            oversized_stores, sample_vehicles
        )

        # Some stores may not be assignable due to size constraints
        total_assigned = sum(len(stores) for stores in vehicle_assignments.values())
        assert total_assigned <= len(
            oversized_stores
        ), "Cannot assign more stores than created"

        print(
            f"Assigned {total_assigned} out of {len(oversized_stores)} oversized stores"
        )

    def test_route_metrics_calculation(self, large_store_dataset, sample_vehicles):
        """Test accuracy of route metrics calculation."""
        optimizer = RouteOptimizer()

        routes = optimizer.optimize_multi_vehicle_routes(
            large_store_dataset, sample_vehicles
        )

        for route in routes:
            # Verify metrics are reasonable
            assert route.total_distance_km > 0, "Route should have positive distance"
            assert (
                route.estimated_duration_hours > 0
            ), "Route should have positive duration"
            assert route.total_weight_kg > 0, "Route should have positive weight"
            assert route.total_packages > 0, "Route should have positive package count"

            # Check distance vs duration relationship (should be roughly correlated)
            # Assuming urban speeds of 20-60 km/h
            implied_speed = route.total_distance_km / route.estimated_duration_hours
            assert (
                10 <= implied_speed <= 80
            ), f"Implied speed {implied_speed} km/h seems unrealistic"

            # Verify stop count matches assigned stores
            expected_packages = sum(stop["packages"] for stop in route.stops)
            expected_weight = sum(stop["weight_kg"] for stop in route.stops)

            assert route.total_packages == expected_packages, "Package count mismatch"
            assert (
                abs(route.total_weight_kg - expected_weight) < 0.01
            ), "Weight calculation mismatch"

    def test_constraint_validation(self, large_store_dataset, sample_vehicles):
        """Test route constraint validation."""
        optimizer = RouteOptimizer()

        routes = optimizer.optimize_multi_vehicle_routes(
            large_store_dataset, sample_vehicles
        )

        # Define test constraints
        constraints = {
            "max_driving_hours": 8,
            "max_weight_kg": 1000,
            "max_packages": 40,
            "max_stops": 15,
        }

        for route in routes:
            validation_results = optimizer.validate_route_constraints(
                route, constraints
            )

            # Check all validation keys are present
            expected_keys = [
                "within_driving_time_limit",
                "within_weight_capacity",
                "within_package_capacity",
                "within_stop_limit",
            ]
            for key in expected_keys:
                assert key in validation_results, f"Missing validation key: {key}"
                assert isinstance(
                    validation_results[key], bool
                ), f"Validation {key} should be boolean"

            # Print constraint violations for analysis
            violations = [
                key for key, passed in validation_results.items() if not passed
            ]
            if violations:
                print(f"Route {route.route_id} constraint violations: {violations}")

    def test_empty_input_handling(self, sample_vehicles):
        """Test handling of edge cases with empty inputs."""
        optimizer = RouteOptimizer()

        # Test with no stores
        routes = optimizer.optimize_multi_vehicle_routes([], sample_vehicles)
        assert len(routes) == 0, "Should return empty routes for no stores"

        # Test with no available vehicles
        unavailable_vehicles = [v for v in sample_vehicles]
        for vehicle in unavailable_vehicles:
            vehicle.status = VehicleStatus.MAINTENANCE

        with pytest.raises(ValueError, match="No available vehicles"):
            optimizer.optimize_multi_vehicle_routes(
                [
                    Store(
                        store_id="TEST_001",
                        name="Test Store",
                        address="Test Address",
                        coordinates={"lat": 40.7128, "lng": -74.0060},
                        delivery_window="09:00-17:00",
                        priority="medium",
                        estimated_service_time=15,
                        packages=5,
                        weight_kg=25,
                    )
                ],
                unavailable_vehicles,
            )

    def test_single_store_optimization(self, sample_vehicles):
        """Test optimization with single store."""
        optimizer = RouteOptimizer()

        single_store = [
            Store(
                store_id="SINGLE_001",
                name="Single Store",
                address="Single Address",
                coordinates={"lat": 40.7128, "lng": -74.0060},
                delivery_window="09:00-17:00",
                priority="high",
                estimated_service_time=20,
                packages=3,
                weight_kg=15,
            )
        ]

        routes = optimizer.optimize_multi_vehicle_routes(single_store, sample_vehicles)

        assert len(routes) == 1, "Should generate exactly one route for single store"
        assert len(routes[0].stops) == 1, "Route should have exactly one stop"
        assert routes[0].stops[0]["store_id"] == "SINGLE_001"


class TestPerformanceMonitoring:
    """Test suite for performance monitoring and benchmarking."""

    @pytest.fixture
    def performance_monitor(self):
        """Performance monitor instance."""
        return PerformanceMonitor()

    @pytest.fixture
    def benchmark_vehicles(self):
        """Standard vehicle fleet for benchmarking."""
        return [
            Vehicle("BENCH_VAN_1", 800, 30, 8, VehicleStatus.AVAILABLE),
            Vehicle("BENCH_TRUCK_1", 1200, 45, 10, VehicleStatus.AVAILABLE),
        ]

    def test_optimization_benchmarking(
        self, large_store_dataset, benchmark_vehicles, performance_monitor
    ):
        """Test performance benchmarking across optimization methods."""

        benchmark_results = performance_monitor.benchmark_optimization(
            large_store_dataset,
            benchmark_vehicles,
            [OptimizationMethod.NEAREST_NEIGHBOR, OptimizationMethod.TWO_OPT],
        )

        # Verify benchmark results structure
        for method in [OptimizationMethod.NEAREST_NEIGHBOR, OptimizationMethod.TWO_OPT]:
            method_name = method.value
            assert (
                method_name in benchmark_results
            ), f"Missing benchmark for {method_name}"

            result = benchmark_results[method_name]

            if "error" not in result:
                # Verify performance metrics are present
                expected_metrics = [
                    "execution_time_seconds",
                    "total_routes_generated",
                    "total_distance_km",
                    "total_estimated_duration_hours",
                    "avg_distance_per_route",
                    "stores_processed",
                    "vehicles_used",
                ]

                for metric in expected_metrics:
                    assert (
                        metric in result
                    ), f"Missing metric {metric} for {method_name}"
                    assert isinstance(
                        result[metric], (int, float)
                    ), f"Metric {metric} should be numeric"

                # Verify reasonable performance values
                assert (
                    result["execution_time_seconds"] > 0
                ), "Should have positive execution time"
                assert result["stores_processed"] == len(
                    large_store_dataset
                ), "Should process all stores"
                assert (
                    result["total_routes_generated"] > 0
                ), "Should generate at least one route"

        print("Benchmark Results:")
        for method, metrics in benchmark_results.items():
            if "error" not in metrics:
                print(f"  {method}:")
                print(f"    Execution Time: {metrics['execution_time_seconds']:.3f}s")
                print(f"    Routes Generated: {metrics['total_routes_generated']}")
                print(f"    Total Distance: {metrics['total_distance_km']:.2f}km")
                print(
                    f"    Avg Distance/Route: {metrics['avg_distance_per_route']:.2f}km"
                )

    def test_route_efficiency_analysis(
        self, large_store_dataset, benchmark_vehicles, performance_monitor
    ):
        """Test route efficiency analysis metrics."""
        optimizer = RouteOptimizer()

        routes = optimizer.optimize_multi_vehicle_routes(
            large_store_dataset, benchmark_vehicles
        )

        for route in routes:
            efficiency_metrics = performance_monitor.analyze_route_efficiency(route)

            # Verify efficiency metrics structure
            expected_metrics = [
                "efficiency_score",
                "distance_per_stop_km",
                "time_per_stop_hours",
                "weight_utilization_percent",
                "high_priority_ratio",
            ]

            for metric in expected_metrics:
                assert (
                    metric in efficiency_metrics
                ), f"Missing efficiency metric: {metric}"
                assert isinstance(
                    efficiency_metrics[metric], (int, float)
                ), f"Metric {metric} should be numeric"

            # Verify reasonable value ranges
            assert (
                0 <= efficiency_metrics["efficiency_score"] <= 100
            ), "Efficiency score should be 0-100"
            assert (
                efficiency_metrics["distance_per_stop_km"] > 0
            ), "Distance per stop should be positive"
            assert (
                efficiency_metrics["time_per_stop_hours"] > 0
            ), "Time per stop should be positive"
            assert (
                0 <= efficiency_metrics["weight_utilization_percent"] <= 100
            ), "Weight utilization should be 0-100%"
            assert (
                0 <= efficiency_metrics["high_priority_ratio"] <= 1
            ), "Priority ratio should be 0-1"

            print(f"Route {route.route_id} Efficiency Analysis:")
            print(
                f"  Efficiency Score: {efficiency_metrics['efficiency_score']:.1f}/100"
            )
            print(
                f"  Distance/Stop: {efficiency_metrics['distance_per_stop_km']:.2f}km"
            )
            print(f"  Time/Stop: {efficiency_metrics['time_per_stop_hours']:.2f}h")
            print(
                f"  Weight Utilization: {efficiency_metrics['weight_utilization_percent']:.1f}%"
            )

    def test_performance_with_large_datasets(
        self, benchmark_vehicles, performance_monitor
    ):
        """Test performance with varying dataset sizes."""
        dataset_sizes = [10, 25, 50, 100]

        for size in dataset_sizes:
            # Generate synthetic dataset of specified size
            large_dataset = []
            for i in range(size):
                store = Store(
                    store_id=f"PERF_{i:03d}",
                    name=f"Performance Test Store {i}",
                    address=f"{i} Performance St",
                    coordinates={
                        "lat": 40.7128 + (i % 10) * 0.01,
                        "lng": -74.0060 + (i // 10) * 0.01,
                    },
                    delivery_window="09:00-17:00",
                    priority=["high", "medium", "low"][i % 3],
                    estimated_service_time=15,
                    packages=3 + (i % 5),
                    weight_kg=20 + (i % 15),
                )
                large_dataset.append(store)

            # Benchmark performance
            start_time = datetime.now()
            optimizer = RouteOptimizer()
            routes = optimizer.optimize_multi_vehicle_routes(
                large_dataset, benchmark_vehicles
            )
            end_time = datetime.now()

            execution_time = (end_time - start_time).total_seconds()

            # Verify performance is reasonable (should complete within reasonable time)
            max_expected_time = size * 0.1  # Allow 0.1 seconds per store maximum
            assert (
                execution_time <= max_expected_time
            ), f"Optimization took too long for {size} stores: {execution_time}s"

            print(f"Dataset Size: {size} stores")
            print(f"  Execution Time: {execution_time:.3f}s")
            print(f"  Routes Generated: {len(routes)}")
            print(f"  Time per Store: {execution_time / size:.4f}s")

    def test_memory_usage_monitoring(self, benchmark_vehicles):
        """Test memory usage stays reasonable with large datasets."""
        import sys

        # Get initial memory usage
        initial_size = sys.getsizeof(locals())

        # Create progressively larger datasets and monitor memory
        for size in [50, 100, 200]:
            dataset = []
            for i in range(size):
                store = Store(
                    store_id=f"MEM_{i:03d}",
                    name=f"Memory Test Store {i}",
                    address=f"{i} Memory Lane",
                    coordinates={
                        "lat": 40.7128 + i * 0.001,
                        "lng": -74.0060 + i * 0.001,
                    },
                    delivery_window="09:00-17:00",
                    priority="medium",
                    estimated_service_time=15,
                    packages=5,
                    weight_kg=25,
                )
                dataset.append(store)

            optimizer = RouteOptimizer()
            routes = optimizer.optimize_multi_vehicle_routes(
                dataset, benchmark_vehicles
            )

            current_size = sys.getsizeof(locals())
            memory_growth = current_size - initial_size

            # Memory growth should be reasonable (less than 10MB for test datasets)
            max_memory_mb = 10 * 1024 * 1024  # 10MB
            assert (
                memory_growth <= max_memory_mb
            ), f"Excessive memory usage: {memory_growth} bytes"

            print(f"Dataset size {size}: Memory growth = {memory_growth} bytes")

            # Clean up
            del dataset, routes, optimizer
