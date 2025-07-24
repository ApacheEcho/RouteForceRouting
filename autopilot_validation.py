#!/usr/bin/env python3
"""
AUTO-PILOT: Simplified Performance Validation for RouteForce
Tests core functionality and performance without complex dependencies
"""

import time
import psutil
import json
import logging
from datetime import datetime
import sys
import os

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def test_genetic_algorithm_basic():
    """Test basic genetic algorithm functionality"""
    try:
        from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
        
        # Generate small test dataset
        test_stores = [
            {'id': 1, 'latitude': 40.7128, 'longitude': -74.0060, 'name': 'Store 1'},
            {'id': 2, 'latitude': 40.7589, 'longitude': -73.9851, 'name': 'Store 2'},
            {'id': 3, 'latitude': 40.6892, 'longitude': -74.0445, 'name': 'Store 3'},
            {'id': 4, 'latitude': 40.7831, 'longitude': -73.9712, 'name': 'Store 4'},
            {'id': 5, 'latitude': 40.7484, 'longitude': -73.9857, 'name': 'Store 5'}
        ]
        
        config = GeneticConfig(population_size=20, generations=50)
        ga = GeneticAlgorithm(config)
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        optimized_route, metrics = ga.optimize(test_stores)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        execution_time = end_time - start_time
        memory_delta = (end_memory - start_memory) / (1024 * 1024)
        
        return {
            'status': 'success',
            'execution_time': execution_time,
            'memory_usage_mb': memory_delta,
            'improvement_percent': metrics.get('improvement_percent', 0),
            'generations_completed': metrics.get('generations', 0),
            'route_count': len(optimized_route)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def test_system_performance():
    """Test system performance metrics"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'status': 'success',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_free_gb': disk.free / (1024**3),
            'system_healthy': cpu_percent < 80 and memory.percent < 80
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def test_application_imports():
    """Test critical application imports"""
    import_results = {}
    
    modules_to_test = [
        'app.optimization.genetic_algorithm',
        'app.services.geocoding_cache',
        'app.performance.optimization_engine',
        'app.database.optimized_connection_pool'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            import_results[module] = 'success'
        except Exception as e:
            import_results[module] = f'error: {str(e)}'
    
    return import_results

def test_frontend_build():
    """Test frontend build status"""
    try:
        frontend_dist = 'frontend/dist'
        
        if not os.path.exists(frontend_dist):
            return {
                'status': 'error',
                'error': 'Frontend dist directory not found'
            }
        
        # Check for key files
        key_files = ['index.html']
        assets_dir = os.path.join(frontend_dist, 'assets')
        
        files_found = []
        for file in key_files:
            if os.path.exists(os.path.join(frontend_dist, file)):
                files_found.append(file)
        
        # Check assets directory
        assets_count = 0
        if os.path.exists(assets_dir):
            assets_count = len([f for f in os.listdir(assets_dir) 
                              if f.endswith(('.js', '.css'))])
        
        # Calculate total size
        total_size = 0
        for root, dirs, files in os.walk(frontend_dist):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        
        return {
            'status': 'success',
            'key_files_found': files_found,
            'assets_count': assets_count,
            'total_size_mb': total_size / (1024 * 1024),
            'build_complete': len(files_found) > 0 and assets_count > 0
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def test_deployment_readiness():
    """Test deployment readiness"""
    try:
        # Check netlify.toml
        netlify_config = os.path.exists('netlify.toml')
        
        # Check package.json in frontend
        frontend_package = os.path.exists('frontend/package.json')
        
        # Check main app files
        main_files = ['app.py', 'app/__init__.py']
        main_files_exist = all(os.path.exists(f) for f in main_files)
        
        return {
            'status': 'success',
            'netlify_config': netlify_config,
            'frontend_package': frontend_package,
            'main_files': main_files_exist,
            'ready_for_deployment': netlify_config and frontend_package and main_files_exist
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def run_autopilot_validation():
    """Run complete AUTO-PILOT validation suite"""
    print("🚀 AUTO-PILOT: Performance Validation Suite")
    print("=" * 50)
    
    start_time = time.time()
    
    # Test suite
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'system_info': {
            'python_version': sys.version,
            'platform': sys.platform
        }
    }
    
    print("\n📊 Testing Genetic Algorithm...")
    results['genetic_algorithm'] = test_genetic_algorithm_basic()
    if results['genetic_algorithm']['status'] == 'success':
        print(f"   ✅ GA Test: {results['genetic_algorithm']['execution_time']:.2f}s")
    else:
        print(f"   ❌ GA Test Failed: {results['genetic_algorithm']['error']}")
    
    print("\n📊 Testing System Performance...")
    results['system_performance'] = test_system_performance()
    if results['system_performance']['status'] == 'success':
        print(f"   ✅ System Health: CPU {results['system_performance']['cpu_percent']:.1f}%")
    else:
        print(f"   ❌ System Test Failed: {results['system_performance']['error']}")
    
    print("\n📊 Testing Application Imports...")
    results['imports'] = test_application_imports()
    success_count = sum(1 for v in results['imports'].values() if v == 'success')
    print(f"   ✅ Imports: {success_count}/{len(results['imports'])} successful")
    
    print("\n📊 Testing Frontend Build...")
    results['frontend_build'] = test_frontend_build()
    if results['frontend_build']['status'] == 'success':
        print(f"   ✅ Frontend: {results['frontend_build']['total_size_mb']:.1f}MB")
    else:
        print(f"   ❌ Frontend Test Failed: {results['frontend_build']['error']}")
    
    print("\n📊 Testing Deployment Readiness...")
    results['deployment'] = test_deployment_readiness()
    if results['deployment']['status'] == 'success':
        ready = results['deployment']['ready_for_deployment']
        print(f"   {'✅' if ready else '⚠️'} Deployment Ready: {ready}")
    else:
        print(f"   ❌ Deployment Test Failed: {results['deployment']['error']}")
    
    total_time = time.time() - start_time
    results['total_test_time'] = total_time
    
    # Calculate overall score
    scores = []
    if results['genetic_algorithm']['status'] == 'success':
        scores.append(80)  # High weight for core functionality
    if results['system_performance']['status'] == 'success':
        scores.append(60)
    if results['frontend_build']['status'] == 'success':
        scores.append(70)
    if results['deployment']['status'] == 'success':
        scores.append(50)
    
    overall_score = sum(scores) / 4 if scores else 0
    results['overall_score'] = overall_score
    
    print(f"\n🎯 AUTO-PILOT VALIDATION COMPLETE")
    print(f"⏱️  Total Time: {total_time:.2f} seconds")
    print(f"📊 Overall Score: {overall_score:.1f}/100")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"autopilot_validation_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Results saved: {filename}")
    
    return results

if __name__ == "__main__":
    try:
        results = run_autopilot_validation()
        exit_code = 0 if results['overall_score'] > 50 else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ AUTO-PILOT VALIDATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
