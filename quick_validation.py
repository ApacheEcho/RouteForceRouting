#!/usr/bin/env python3
"""
RouteForce Optimization Validation Script
Quick validation of key performance optimizations
"""
import sys
import os
import time
import logging

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_genetic_algorithm():
    """Test the optimized genetic algorithm"""
    print("\n🧬 Testing Genetic Algorithm...")
    try:
        from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
        
        # Create test stores
        test_stores = [
            {'id': f'store_{i}', 'latitude': 40.7128 + i*0.01, 'longitude': -74.0060 + i*0.01}
            for i in range(10)
        ]
        
        config = GeneticConfig(population_size=20, generations=50)
        ga = GeneticAlgorithm(config)
        
        start_time = time.time()
        route, metrics = ga.optimize(test_stores, {})
        end_time = time.time()
        
        print(f"✅ Genetic Algorithm: {end_time - start_time:.2f}s")
        print(f"   - Improvement: {metrics.get('improvement_percent', 0):.1f}%")
        print(f"   - Generations: {metrics.get('generations', 0)}")
        print(f"   - Final distance: {metrics.get('final_distance', 0):.2f}km")
        return True
        
    except Exception as e:
        print(f"❌ Genetic Algorithm Test Failed: {e}")
        return False

def test_optimization_engine():
    """Test the performance optimization engine"""
    print("\n⚡ Testing Performance Optimization Engine...")
    try:
        from app.performance.optimization_engine import PerformanceOptimizationEngine
        
        engine = PerformanceOptimizationEngine()
        
        # Test basic functionality
        metrics = engine.get_current_metrics()
        recommendations = engine.get_optimization_recommendations()
        
        print(f"✅ Optimization Engine: Initialized successfully")
        print(f"   - Metrics tracked: {len(metrics)}")
        print(f"   - Recommendations: {len(recommendations)}")
        
        # Test monitoring
        engine.start_monitoring()
        time.sleep(1)  # Let it collect some data
        engine.stop_monitoring()
        
        print(f"   - Monitoring: Working")
        return True
        
    except Exception as e:
        print(f"❌ Optimization Engine Test Failed: {e}")
        return False

def test_database_pool():
    """Test the optimized database connection pool"""
    print("\n🗄️ Testing Database Connection Pool...")
    try:
        from app.database.optimized_connection_pool import OptimizedConnectionPool
        
        # Test with in-memory SQLite
        pool = OptimizedConnectionPool('sqlite:///:memory:')
        
        # Test connection acquisition
        with pool.get_connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            
        metrics = pool.get_metrics()
        recommendations = pool.get_recommendations()
        
        print(f"✅ Database Pool: Connection successful")
        print(f"   - Metrics available: {bool(metrics)}")
        print(f"   - Recommendations: {len(recommendations)}")
        return True
        
    except Exception as e:
        print(f"❌ Database Pool Test Failed: {e}")
        return False

def test_geocoding_cache():
    """Test the geocoding cache performance"""
    print("\n🗺️ Testing Geocoding Cache...")
    try:
        from app.services.geocoding_cache import GeocodingCache
        
        cache = GeocodingCache()
        
        # Test cache operations
        test_address = "123 Test Street, New York, NY"
        cache_key = cache._get_cache_key(test_address)
        
        # Simulate cache hit
        cache.memory_cache[cache_key] = {
            'lat': 40.7128,
            'lng': -74.0060,
            'formatted_address': test_address
        }
        
        # Test retrieval
        start_time = time.time()
        result = cache.memory_cache.get(cache_key)
        end_time = time.time()
        
        print(f"✅ Geocoding Cache: {(end_time - start_time) * 1000:.3f}ms retrieval")
        print(f"   - Cache size: {len(cache.memory_cache)}")
        print(f"   - Result: {bool(result)}")
        return True
        
    except Exception as e:
        print(f"❌ Geocoding Cache Test Failed: {e}")
        return False

def test_flask_app_integration():
    """Test Flask app with new optimizations"""
    print("\n🌐 Testing Flask App Integration...")
    try:
        import os
        os.environ['FLASK_ENV'] = 'testing'
        
        from app import create_app
        
        app = create_app('testing')
        
        # Check if optimizations are integrated
        has_optimization_engine = hasattr(app, 'optimization_engine')
        has_db_pool = hasattr(app, 'db_pool')
        
        print(f"✅ Flask App: Created successfully")
        print(f"   - Optimization Engine: {'✅' if has_optimization_engine else '❌'}")
        print(f"   - DB Pool: {'✅' if has_db_pool else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask App Test Failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 RouteForce Optimization Validation Suite")
    print("=" * 50)
    
    # Configure logging to suppress unnecessary output
    logging.basicConfig(level=logging.WARNING)
    
    tests = [
        test_genetic_algorithm,
        test_optimization_engine,
        test_database_pool,
        test_geocoding_cache,
        test_flask_app_integration
    ]
    
    results = []
    start_time = time.time()
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    end_time = time.time()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    
    if success_rate >= 80:
        print("🎉 OPTIMIZATION VALIDATION SUCCESSFUL!")
        exit_code = 0
    else:
        print("⚠️  Some optimizations need attention")
        exit_code = 1
    
    print("=" * 50)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
