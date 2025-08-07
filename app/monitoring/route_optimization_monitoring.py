"""
Enhanced Route Optimization with Sentry Monitoring
Example integration showing how to add Sentry monitoring to route optimization algorithms
"""

from functools import wraps
import time
import tracemalloc
from app.monitoring import SentryHelper, SentryContext, monitor_performance


class SentryMonitoredOptimizer:
    """Base class for route optimizers with Sentry monitoring"""
    
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name
        self.sentry = SentryHelper()
    
    @monitor_performance()
    def optimize(self, locations, constraints=None):
        """
        Main optimization method with comprehensive Sentry monitoring
        """
        with SentryContext(
            f"{self.algorithm_name}_optimization",
            algorithm=self.algorithm_name,
            location_count=len(locations)
        ) as ctx:
            
            try:
                # Set optimization context
                ctx.set_context("optimization", {
                    "algorithm": self.algorithm_name,
                    "location_count": len(locations),
                    "has_constraints": bool(constraints),
                    "constraints": constraints or {}
                })
                
                # Add breadcrumb for start
                ctx.add_breadcrumb(
                    f"Starting {self.algorithm_name} optimization",
                    category="algorithm",
                    level="info",
                    data={"location_count": len(locations)}
                )
                
                # Start performance monitoring
                start_time = time.time()
                tracemalloc.start()
                
                # Perform the actual optimization
                result = self._perform_optimization(locations, constraints)
                
                # Capture performance metrics
                end_time = time.time()
                execution_time = end_time - start_time
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                # Send performance metrics to Sentry
                self.sentry.capture_performance_metrics(
                    self.algorithm_name,
                    execution_time,
                    peak / 1024 / 1024,  # Convert to MB
                    len(locations)
                )
                
                # Add success breadcrumb
                ctx.add_breadcrumb(
                    f"{self.algorithm_name} optimization completed",
                    category="algorithm",
                    level="info",
                    data={
                        "execution_time": execution_time,
                        "memory_usage_mb": peak / 1024 / 1024,
                        "result_quality": self._evaluate_result_quality(result)
                    }
                )
                
                return result
                
            except Exception as e:
                # Capture optimization-specific error
                self.sentry.capture_route_optimization_error(
                    self.algorithm_name,
                    len(locations),
                    e
                )
                
                # Add error breadcrumb
                ctx.add_breadcrumb(
                    f"Error in {self.algorithm_name} optimization",
                    category="algorithm",
                    level="error",
                    data={
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                )
                
                raise
    
    def _perform_optimization(self, locations, constraints):
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement _perform_optimization")
    
    def _evaluate_result_quality(self, result):
        """Evaluate the quality of the optimization result"""
        if not result:
            return 0.0
        
        # Basic quality metrics - override in subclasses for specific algorithms
        return 1.0 if result.get('route') else 0.5


class SentryGeneticAlgorithmOptimizer(SentryMonitoredOptimizer):
    """Genetic Algorithm optimizer with Sentry monitoring"""
    
    def __init__(self):
        super().__init__("genetic_algorithm")
        self.population_size = 100
        self.generations = 50
        self.mutation_rate = 0.01
    
    def _perform_optimization(self, locations, constraints):
        """Genetic algorithm implementation with monitoring"""
        
        # Add algorithm-specific context
        with SentryContext("genetic_algorithm_execution") as ctx:
            ctx.set_context("genetic_algorithm", {
                "population_size": self.population_size,
                "generations": self.generations,
                "mutation_rate": self.mutation_rate
            })
            
            # Simulate genetic algorithm steps with monitoring
            best_route = None
            best_fitness = float('inf')
            
            for generation in range(self.generations):
                # Add breadcrumb for generation progress
                if generation % 10 == 0:  # Every 10 generations
                    ctx.add_breadcrumb(
                        f"Generation {generation}/{self.generations}",
                        category="genetic_algorithm",
                        data={"current_best_fitness": best_fitness}
                    )
                
                # Simulate population evolution
                # (Replace with actual genetic algorithm implementation)
                current_fitness = self._simulate_fitness_calculation(locations)
                
                if current_fitness < best_fitness:
                    best_fitness = current_fitness
                    best_route = self._generate_route_from_fitness(locations, current_fitness)
            
            return {
                "route": best_route,
                "fitness": best_fitness,
                "algorithm": "genetic_algorithm",
                "generations_completed": self.generations
            }
    
    def _simulate_fitness_calculation(self, locations):
        """Simulate fitness calculation (replace with actual implementation)"""
        import random
        return random.uniform(100, 1000)
    
    def _generate_route_from_fitness(self, locations, fitness):
        """Generate route from fitness score (replace with actual implementation)"""
        return [{"lat": loc.get("lat"), "lng": loc.get("lng")} for loc in locations]


class SentrySimulatedAnnealingOptimizer(SentryMonitoredOptimizer):
    """Simulated Annealing optimizer with Sentry monitoring"""
    
    def __init__(self):
        super().__init__("simulated_annealing")
        self.initial_temperature = 1000
        self.cooling_rate = 0.95
        self.min_temperature = 1
    
    def _perform_optimization(self, locations, constraints):
        """Simulated annealing implementation with monitoring"""
        
        with SentryContext("simulated_annealing_execution") as ctx:
            ctx.set_context("simulated_annealing", {
                "initial_temperature": self.initial_temperature,
                "cooling_rate": self.cooling_rate,
                "min_temperature": self.min_temperature
            })
            
            current_solution = self._generate_initial_solution(locations)
            current_energy = self._calculate_energy(current_solution)
            
            best_solution = current_solution.copy()
            best_energy = current_energy
            
            temperature = self.initial_temperature
            iterations = 0
            
            while temperature > self.min_temperature:
                iterations += 1
                
                # Add breadcrumb for temperature milestones
                if iterations % 100 == 0:
                    ctx.add_breadcrumb(
                        f"Iteration {iterations}, Temperature: {temperature:.2f}",
                        category="simulated_annealing",
                        data={
                            "current_energy": current_energy,
                            "best_energy": best_energy,
                            "temperature": temperature
                        }
                    )
                
                # Generate neighbor solution
                neighbor_solution = self._generate_neighbor(current_solution)
                neighbor_energy = self._calculate_energy(neighbor_solution)
                
                # Accept or reject the neighbor
                if self._accept_solution(current_energy, neighbor_energy, temperature):
                    current_solution = neighbor_solution
                    current_energy = neighbor_energy
                    
                    if current_energy < best_energy:
                        best_solution = current_solution.copy()
                        best_energy = current_energy
                
                # Cool down
                temperature *= self.cooling_rate
            
            return {
                "route": best_solution,
                "energy": best_energy,
                "algorithm": "simulated_annealing",
                "iterations": iterations,
                "final_temperature": temperature
            }
    
    def _generate_initial_solution(self, locations):
        """Generate initial solution (replace with actual implementation)"""
        return list(range(len(locations)))
    
    def _calculate_energy(self, solution):
        """Calculate solution energy (replace with actual implementation)"""
        import random
        return random.uniform(100, 1000)
    
    def _generate_neighbor(self, solution):
        """Generate neighbor solution (replace with actual implementation)"""
        import random
        neighbor = solution.copy()
        if len(neighbor) > 1:
            i, j = random.sample(range(len(neighbor)), 2)
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor
    
    def _accept_solution(self, current_energy, neighbor_energy, temperature):
        """Accept or reject solution based on simulated annealing criteria"""
        import random
        import math
        
        if neighbor_energy < current_energy:
            return True
        
        probability = math.exp(-(neighbor_energy - current_energy) / temperature)
        return random.random() < probability


# Flask route integration example
def create_sentry_monitored_routes(app):
    """Create Flask routes with Sentry monitoring"""
    
    @app.route('/api/optimize/genetic', methods=['POST'])
    def optimize_genetic():
        """Genetic algorithm optimization endpoint with Sentry monitoring"""
        from flask import request, jsonify
        
        try:
            # Capture API usage
            start_time = time.time()
            
            data = request.get_json()
            locations = data.get('locations', [])
            constraints = data.get('constraints', {})
            
            # Initialize optimizer with monitoring
            optimizer = SentryGeneticAlgorithmOptimizer()
            
            # Perform optimization
            result = optimizer.optimize(locations, constraints)
            
            # Capture API performance
            response_time = time.time() - start_time
            SentryHelper.capture_api_usage(
                '/api/optimize/genetic',
                response_time,
                200,
                request.headers.get('X-User-ID')
            )
            
            return jsonify({
                "success": True,
                "result": result,
                "execution_time": response_time
            })
            
        except Exception as e:
            # Capture API error
            response_time = time.time() - start_time if 'start_time' in locals() else 0
            SentryHelper.capture_api_usage(
                '/api/optimize/genetic',
                response_time,
                500,
                request.headers.get('X-User-ID')
            )
            
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/optimize/annealing', methods=['POST'])
    def optimize_annealing():
        """Simulated annealing optimization endpoint with Sentry monitoring"""
        from flask import request, jsonify
        
        try:
            start_time = time.time()
            
            data = request.get_json()
            locations = data.get('locations', [])
            constraints = data.get('constraints', {})
            
            optimizer = SentrySimulatedAnnealingOptimizer()
            result = optimizer.optimize(locations, constraints)
            
            response_time = time.time() - start_time
            SentryHelper.capture_api_usage(
                '/api/optimize/annealing',
                response_time,
                200,
                request.headers.get('X-User-ID')
            )
            
            return jsonify({
                "success": True,
                "result": result,
                "execution_time": response_time
            })
            
        except Exception as e:
            response_time = time.time() - start_time if 'start_time' in locals() else 0
            SentryHelper.capture_api_usage(
                '/api/optimize/annealing',
                response_time,
                500,
                request.headers.get('X-User-ID')
            )
            
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
