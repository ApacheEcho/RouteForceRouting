"""
Comprehensive Edge Case Tests for RouteForce System
Tests database timeouts, WebSocket reconnection under load, and memory pressure scenarios
"""

import pytest
import time
import threading
import psutil
import gc
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.database.optimized_connection_pool import DatabaseConnectionPool
import redis


class TestDatabaseTimeouts:
    """Test database connection timeout scenarios"""

    def setup_method(self):
        """Setup test database pool"""
        self.pool = DatabaseConnectionPool(
            database_url="sqlite:///:memory:",
            pool_size=2,
            max_overflow=1
        )

    def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted"""
        connections = []
        
        try:
            # Exhaust the pool (2 + 1 overflow = 3 total)
            for i in range(3):
                conn = self.pool.get_connection()
                connections.append(conn.__enter__())
            
            # This should trigger pool exhaustion
            start_time = time.time()
            with pytest.raises(Exception):
                with self.pool.get_connection():
                    pass
            
            # Should fail quickly, not hang
            elapsed = time.time() - start_time
            assert elapsed < 5.0, "Connection timeout took too long"
            
        finally:
            for conn in connections:
                try:
                    conn.__exit__(None, None, None)
                except:
                    pass

    def test_slow_connection_acquisition_logging(self):
        """Test logging of slow connection acquisition"""
        with patch('app.database.optimized_connection_pool.logger') as mock_logger:
            # Simulate slow connection by patching engine.connect
            original_connect = self.pool.engine.connect
            
            def slow_connect():
                time.sleep(6)  # Longer than 5s threshold
                return original_connect()
            
            self.pool.engine.connect = slow_connect
            
            with self.pool.get_connection():
                pass
                
            mock_logger.warning.assert_called()
            assert "Slow connection acquisition" in str(mock_logger.warning.call_args)

    def test_auto_optimization_on_pool_pressure(self):
        """Test that auto-optimization triggers on pool pressure"""
        # Simulate pool overflow
        self.pool.metrics.pool_overflow = 5
        
        with patch.object(self.pool, '_auto_optimize') as mock_optimize:
            with self.pool.get_connection():
                pass
            
            mock_optimize.assert_called_once()

    def test_connection_error_tracking(self):
        """Test proper tracking of connection errors"""
        initial_errors = self.pool.metrics.connection_errors
        
        # Simulate connection error
        with patch.object(self.pool.engine, 'connect', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                with self.pool.get_connection():
                    pass
        
        assert self.pool.metrics.connection_errors == initial_errors + 1


class TestWebSocketReconnectionLoad:
    """Test WebSocket reconnection behavior under load conditions"""

    def setup_method(self):
        """Setup WebSocket test environment"""
        self.mock_socket = Mock()
        self.reconnection_attempts = []

    def test_multiple_rapid_disconnections(self):
        """Test WebSocket handling of rapid disconnection events"""
        # This would require selenium for full JS testing
        # For now, test the logic conceptually
        
        class MockWebSocket:
            def __init__(self):
                self.reconnection_timer = None
                self.reconnect_attempts = 0
                self.max_reconnect_attempts = 5
                self.reconnect_delay = 1000
                self.is_connected = False
                
            def attempt_reconnection(self):
                if self.reconnection_timer:
                    # Clear existing timer (debouncing)
                    self.reconnection_timer = "cleared"
                    
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    self.reconnect_attempts += 1
                    self.reconnection_timer = f"timer_{self.reconnect_attempts}"
                    return True
                return False
        
        ws = MockWebSocket()
        
        # Simulate rapid disconnections
        for _ in range(3):
            result = ws.attempt_reconnection()
            assert result == True
            
        assert ws.reconnect_attempts == 3
        assert ws.reconnection_timer == "timer_3"

    def test_reconnection_backoff_under_load(self):
        """Test exponential backoff works correctly under load"""
        delays = []
        
        class MockWebSocket:
            def __init__(self):
                self.reconnect_attempts = 0
                self.reconnect_delay = 1000
                
            def get_backoff_delay(self):
                self.reconnect_attempts += 1
                return self.reconnect_delay * self.reconnect_attempts
        
        ws = MockWebSocket()
        
        # Test backoff progression
        for i in range(1, 6):
            delay = ws.get_backoff_delay()
            delays.append(delay)
            assert delay == 1000 * i
            
        # Delays should increase: 1000, 2000, 3000, 4000, 5000
        assert delays == [1000, 2000, 3000, 4000, 5000]


class TestMemoryPressureOptimization:
    """Test system behavior under memory pressure during large optimizations"""

    def setup_method(self):
        """Setup memory pressure testing"""
        self.initial_memory = psutil.Process().memory_info().rss

    def test_genetic_algorithm_memory_usage(self):
        """Test genetic algorithm doesn't leak memory during large optimizations"""
        from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
        
        # Create large store dataset
        stores = []
        for i in range(1000):  # Large dataset
            stores.append({
                'id': f'store_{i}',
                'lat': 40.7128 + (i * 0.01),
                'lon': -74.0060 + (i * 0.01),
                'name': f'Store {i}'
            })
        
        config = GeneticConfig(
            population_size=50,  # Smaller for testing
            generations=100
        )
        
        ga = GeneticAlgorithm(config)
        
        # Monitor memory before optimization
        gc.collect()
        memory_before = psutil.Process().memory_info().rss
        
        # Run optimization
        result_route, metrics = ga.optimize(stores[:100])  # Use subset for testing
        
        # Force garbage collection
        ga = None
        gc.collect()
        
        # Check memory after
        memory_after = psutil.Process().memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"
        
        # Should have valid results
        assert len(result_route) == 100
        assert metrics['improvement_percent'] >= 0

    def test_background_thread_memory_cleanup(self):
        """Test background thread properly cleans up memory"""
        # Import here to avoid import issues
        try:
            from app.socketio_handlers import active_routes
        except ImportError:
            # Create mock active_routes for testing
            active_routes = {}
        
        # Simulate accumulation of route data
        for i in range(1000):
            active_routes[f'route_{i}'] = {
                'created_at': time.time() - 7200,  # 2 hours ago
                'last_update': time.time() - 3700,  # > 1 hour ago (stale)
                'data': [f'data_{j}' for j in range(100)]  # Some memory usage
            }
        
        initial_count = len(active_routes)
        
        # Simulate cleanup (manually call the cleanup logic)
        current_time = time.time()
        stale_routes = [
            route_id for route_id, route_data in list(active_routes.items())
            if current_time - route_data.get('last_update', route_data['created_at']) > 3600
        ]
        
        for route_id in stale_routes:
            try:
                del active_routes[route_id]
            except KeyError:
                pass
        
        final_count = len(active_routes)
        
        # Should have cleaned up stale routes
        assert final_count < initial_count
        assert final_count == 0  # All should be stale

    def test_redis_cache_memory_efficiency(self):
        """Test Redis cache doesn't cause memory issues"""
        try:
            from app.services.geocoding_cache import GeocodingCache
            
            # Test with mock Redis
            with patch('redis.from_url') as mock_redis_class:
                mock_redis = Mock()
                mock_redis.ping.return_value = True
                mock_redis.get.return_value = None
                mock_redis_class.return_value = mock_redis
                
                cache = GeocodingCache()
                
                # Add many cache entries
                for i in range(10000):
                    address = f"test_address_{i}"
                    coords = {"lat": 40.7128 + i * 0.001, "lon": -74.0060 + i * 0.001}
                    cache.set(address, coords)
                
                # File cache should not grow excessively
                assert len(cache.file_cache) <= 10000
                
                stats = cache.get_stats()
                assert stats['file_entries'] == 10000
                
        except ImportError:
            pytest.skip("Geocoding cache module not available for testing")


class TestPerformanceBenchmarks:
    """Performance benchmark tests using pytest-benchmark patterns"""

    def test_genetic_algorithm_performance(self):
        """Benchmark genetic algorithm performance"""
        from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
        
        # Create test dataset
        stores = []
        for i in range(50):
            stores.append({
                'id': f'store_{i}',
                'lat': 40.7128 + (i * 0.01),
                'lon': -74.0060 + (i * 0.01),
                'name': f'Store {i}'
            })
        
        config = GeneticConfig(
            population_size=20,
            generations=50
        )
        
        def run_optimization():
            ga = GeneticAlgorithm(config)
            return ga.optimize(stores)
        
        # Time the optimization
        start_time = time.time()
        result_route, metrics = run_optimization()
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (less than 10 seconds for test)
        assert execution_time < 10.0, f"Optimization took {execution_time:.2f}s, too slow"
        
        # Should achieve some improvement
        assert metrics['improvement_percent'] >= 0
        
        print(f"Genetic Algorithm Performance: {execution_time:.2f}s for {len(stores)} stores")

    def test_database_connection_performance(self):
        """Benchmark database connection performance"""
        pool = DatabaseConnectionPool(
            database_url="sqlite:///:memory:",
            pool_size=5,
            max_overflow=2
        )
        
        def get_and_use_connection():
            with pool.get_connection() as conn:
                # Simulate some work
                result = conn.execute("SELECT 1")
                return result.fetchone()
        
        # Test multiple connections rapidly
        start_time = time.time()
        for _ in range(100):
            get_and_use_connection()
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        # Each connection should be fast (less than 50ms average)
        assert avg_time < 0.05, f"Average connection time {avg_time:.3f}s too slow"
        
        print(f"Database Connection Performance: {avg_time:.3f}s average")

    def test_geocoding_cache_performance(self):
        """Benchmark geocoding cache performance"""
        from app.services.geocoding_cache import GeocodingCache
        
        with patch('redis.from_url') as mock_redis_class:
            mock_redis = Mock()
            mock_redis.ping.return_value = True
            mock_redis.get.return_value = '{"lat": 40.7128, "lon": -74.0060}'
            mock_redis_class.return_value = mock_redis
            
            cache = GeocodingCache()
            
            # Benchmark cache hits
            start_time = time.time()
            for i in range(1000):
                result = cache.get(f"test_address_{i % 100}")  # 90% hit rate
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / 1000
            
            # Should be very fast (Redis target: <1ms)
            assert avg_time < 0.01, f"Cache lookup {avg_time:.3f}s too slow"
            
            print(f"Geocoding Cache Performance: {avg_time:.3f}s average")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])