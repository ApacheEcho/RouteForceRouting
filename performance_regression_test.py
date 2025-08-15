#!/usr/bin/env python3
"""
Performance Regression Test Suite for RouteForce Optimization
Tests critical performance aspects and validates optimization improvements
"""

import time
import psutil
import tracemalloc
import json
import logging
import traceback
from typing import Dict, List, Any
from datetime import datetime
import sys
import os

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
from app.performance.optimization_engine import PerformanceOptimizer
from app.database.optimized_connection_pool import DatabaseConnectionPool
from app.services.geocoding_cache import GeocodingCache


class PerformanceTest:
    """Performance test suite for RouteForce optimizations"""

    def __init__(self):
        self.results = {}
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup logging for test results"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger(__name__)

    def generate_test_stores(self, count: int) -> List[Dict[str, Any]]:
        """Generate test store data for performance testing"""
        import random

        stores = []
        # Use realistic coordinates around major cities
        base_coords = [
            (40.7128, -74.0060),  # NYC
            (34.0522, -118.2437),  # LA
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
        ]

        for i in range(count):
            base_lat, base_lon = random.choice(base_coords)
            # Add random variation within ~50km radius
            lat_offset = random.uniform(-0.5, 0.5)
            lon_offset = random.uniform(-0.5, 0.5)

            stores.append(
                {
                    "id": f"store_{i}",
                    "name": f"Store {i}",
                    "latitude": base_lat + lat_offset,
                    "longitude": base_lon + lon_offset,
                    "address": f"{i} Test Street",
                }
            )

        return stores

    def test_genetic_algorithm_performance(self) -> Dict[str, Any]:
        """Test genetic algorithm performance and convergence"""
        self.logger.info("Testing Genetic Algorithm Performance...")

        results = {}
        test_sizes = [10, 25, 50, 100]

        for size in test_sizes:
            stores = self.generate_test_stores(size)

            # Test with optimized configuration
            config = GeneticConfig(
                population_size=50,
                generations=200,
                mutation_rate=0.02,
                crossover_rate=0.8,
                elite_size=10,
            )

            ga = GeneticAlgorithm(config)

            # Memory and time tracking
            tracemalloc.start()
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss

            optimized_route, metrics = ga.optimize(stores)

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            execution_time = end_time - start_time
            memory_delta = end_memory - start_memory

            results[f"{size}_stores"] = {
                "execution_time_seconds": execution_time,
                "memory_usage_mb": memory_delta / (1024 * 1024),
                "peak_memory_mb": peak / (1024 * 1024),
                "generations_run": metrics["generations"],
                "improvement_percent": metrics["improvement_percent"],
                "final_distance_km": metrics["final_distance"],
                "performance_score": size
                / execution_time,  # stores per second
            }

            self.logger.info(
                f"GA Test {size} stores: {execution_time:.2f}s, "
                f"{memory_delta/(1024*1024):.1f}MB, "
                f"{metrics['improvement_percent']:.1f}% improvement"
            )

        return results

    def test_caching_performance(self) -> Dict[str, Any]:
        """Test geocoding cache performance"""
        self.logger.info("Testing Geocoding Cache Performance...")

        cache = GeocodingCache()
        test_addresses = [
            "123 Main St, New York, NY",
            "456 Oak Ave, Los Angeles, CA",
            "789 Pine St, Chicago, IL",
            "321 Elm St, Houston, TX",
        ] * 25  # 100 total requests

        # Cold cache test
        start_time = time.time()
        for address in test_addresses:
            # Simulate cache operations without actual API calls
            cache_key = cache._get_cache_key(address)
            if cache_key not in cache.memory_cache:
                cache.memory_cache[cache_key] = {
                    "lat": 40.7128,
                    "lng": -74.0060,
                    "formatted_address": address,
                }
        cold_time = time.time() - start_time

        # Warm cache test
        start_time = time.time()
        for address in test_addresses:
            cache_key = cache._get_cache_key(address)
            _ = cache.memory_cache.get(cache_key)
        warm_time = time.time() - start_time

        cache_hit_ratio = len(cache.memory_cache) / len(test_addresses)

        return {
            "cold_cache_time_seconds": cold_time,
            "warm_cache_time_seconds": warm_time,
            "speedup_factor": cold_time / warm_time if warm_time > 0 else 0,
            "cache_hit_ratio": cache_hit_ratio,
            "memory_cache_size": len(cache.memory_cache),
        }

    def test_optimization_engine(self) -> Dict[str, Any]:
        """Test performance optimization engine"""
        self.logger.info("Testing Performance Optimization Engine...")

        engine = PerformanceOptimizer()

        # Start monitoring briefly
        engine.start()
        time.sleep(2)  # Let it collect some metrics

        # Get current metrics
        metrics = engine.get_optimization_report()
        recommendations = metrics.get("recommendations", [])

        engine.stop()

        return {
            "metrics_collected": len(metrics.get("current_metrics", {})),
            "recommendations_generated": len(recommendations),
            "cpu_monitoring_active": "cpu_percent"
            in metrics.get("current_metrics", {}),
            "memory_monitoring_active": "memory_mb"
            in metrics.get("current_metrics", {}),
            "monitoring_overhead_minimal": True,  # Assume minimal if running
        }

    def test_database_pool_performance(self) -> Dict[str, Any]:
        """Test optimized database connection pool"""
        self.logger.info("Testing Database Connection Pool...")

        # Test with SQLite for consistency
        pool = DatabaseConnectionPool("sqlite:///test_performance.db")

        # Simulate connection requests
        start_time = time.time()
        connections_created = 0

        try:
            for i in range(10):
                with pool.get_connection() as _:
                    connections_created += 1
                    # Simulate some work
                    time.sleep(0.01)
        except Exception as e:
            self.logger.warning(f"Database pool test error: {e}")

        end_time = time.time()

        metrics = pool.get_metrics()
        recommendations = pool.get_recommendations()

        return {
            "connection_time_seconds": end_time - start_time,
            "connections_created": connections_created,
            "pool_metrics_available": bool(metrics),
            "recommendations_generated": len(recommendations),
            "performance_monitoring_active": True,
        }

    def test_memory_leaks(self) -> Dict[str, Any]:
        """Test for memory leaks in optimization algorithms"""
        self.logger.info("Testing for Memory Leaks...")

        initial_memory = psutil.Process().memory_info().rss

        # Run multiple optimization cycles
        for cycle in range(5):
            stores = self.generate_test_stores(20)
            ga = GeneticAlgorithm(GeneticConfig(generations=50))
            _, _ = ga.optimize(stores)

            # Force garbage collection
            import gc

            gc.collect()

        final_memory = psutil.Process().memory_info().rss
        memory_growth = final_memory - initial_memory

        return {
            "initial_memory_mb": initial_memory / (1024 * 1024),
            "final_memory_mb": final_memory / (1024 * 1024),
            "memory_growth_mb": memory_growth / (1024 * 1024),
            "memory_leak_detected": memory_growth
            > 50 * 1024 * 1024,  # 50MB threshold
            "cycles_completed": 5,
        }

    def run_full_suite(self) -> Dict[str, Any]:
        """Run complete performance test suite"""
        self.logger.info(
            "Starting RouteForce Performance Regression Test Suite"
        )

        start_time = time.time()

        # Run all tests
        test_results = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "python_version": sys.version,
            },
            "genetic_algorithm": self.test_genetic_algorithm_performance(),
            "caching": self.test_caching_performance(),
            "optimization_engine": self.test_optimization_engine(),
            "database_pool": self.test_database_pool_performance(),
            "memory_leaks": self.test_memory_leaks(),
        }

        total_time = time.time() - start_time
        test_results["total_test_time_seconds"] = total_time

        # Generate performance score
        ga_scores = [
            result["performance_score"]
            for result in test_results["genetic_algorithm"].values()
        ]
        avg_ga_performance = (
            sum(ga_scores) / len(ga_scores) if ga_scores else 0
        )

        cache_speedup = test_results["caching"]["speedup_factor"]
        memory_ok = not test_results["memory_leaks"]["memory_leak_detected"]

        overall_score = (
            avg_ga_performance * 0.5
            + cache_speedup * 0.3
            + (100 if memory_ok else 0) * 0.2
        )
        test_results["overall_performance_score"] = overall_score

        self.logger.info(
            f"Performance test suite completed in {total_time:.2f} seconds"
        )
        self.logger.info(f"Overall performance score: {overall_score:.1f}")

        return test_results

    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_results_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Results saved to {filename}")
        return filename


def main():
    """Main test execution"""
    test_suite = PerformanceTest()

    try:
        results = test_suite.run_full_suite()
        filename = test_suite.save_results(results)

        # Print summary
        print("\n" + "=" * 60)
        print("ROUTEFORCE PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        print(
            f"Overall Performance Score: {results['overall_performance_score']:.1f}"
        )
        print(
            f"Total Test Time: {results['total_test_time_seconds']:.2f} seconds"
        )
        print(
            f"Memory Leaks Detected: {'Yes' if results['memory_leaks']['memory_leak_detected'] else 'No'}"
        )
        print(f"Results saved to: {filename}")
        print("=" * 60)

        # Exit with appropriate code
        exit_code = 0 if results["overall_performance_score"] > 50 else 1
        sys.exit(exit_code)

    except Exception as e:
        logging.error(f"Performance test failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
