from celery import group, chord
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict
import redis
from app import celery
from app.optimization.genetic_algorithm import GeneticAlgorithm

class ScaledRouteOptimizer:
    """Handles 1000+ jobs/day with intelligent partitioning"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(app.config['REDIS_URL'])
        self.optimizer = GeneticAlgorithm()
    
    def optimize_large_fleet(self, jobs, fleet_size):
        """Optimize routes for large fleets (up to 500+ vehicles)"""
        # Partition jobs by region/depot for parallel processing
        partitions = self._partition_jobs_by_region(jobs)
        
        # Create Celery group for parallel optimization
        optimization_tasks = group(
            optimize_partition.s(partition, fleet_size // len(partitions))
            for partition in partitions
        )
        
        # Execute with chord for result aggregation
        callback = aggregate_optimization_results.s()
        job = chord(optimization_tasks)(callback)
        
        return job.get(timeout=300)  # 5 minute timeout
    
    def _partition_jobs_by_region(self, jobs, max_partition_size=100):
        """Intelligently partition jobs for scalability"""
        if len(jobs) <= max_partition_size:
            return [jobs]
        
        # Extract coordinates for clustering
        coordinates = np.array([[job.latitude, job.longitude] for job in jobs])
        
        # Determine optimal number of clusters
        n_clusters = max(1, len(jobs) // max_partition_size)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(coordinates)
        
        # Group jobs by cluster
        partitions = defaultdict(list)
        for job, label in zip(jobs, labels):
            partitions[label].append(job)
        
        return list(partitions.values())
    
    def optimize_with_constraints(self, jobs, constraints):
        """Optimize with business constraints"""
        # Apply time windows
        if constraints.get('time_windows'):
            jobs = self._apply_time_windows(jobs, constraints['time_windows'])
        
        # Apply vehicle capacity
        if constraints.get('vehicle_capacity'):
            jobs = self._apply_capacity_constraints(jobs, constraints['vehicle_capacity'])
        
        # Apply driver constraints (DOT compliance)
        if constraints.get('driver_constraints'):
            jobs = self._apply_driver_constraints(jobs, constraints['driver_constraints'])
        
        return self.optimizer.optimize(jobs, constraints)
    
    def _apply_time_windows(self, jobs, time_windows):
        """Filter jobs based on time window constraints"""
        valid_jobs = []
        for job in jobs:
            if self._is_within_time_window(job, time_windows):
                valid_jobs.append(job)
        return valid_jobs
    
    def _apply_capacity_constraints(self, jobs, vehicle_capacity):
        """Group jobs by vehicle capacity"""
        # Sort jobs by weight/volume
        sorted_jobs = sorted(jobs, key=lambda x: x.weight, reverse=True)
        
        # Bin packing algorithm
        vehicles = []
        current_vehicle = []
        current_capacity = 0
        
        for job in sorted_jobs:
            if current_capacity + job.weight <= vehicle_capacity:
                current_vehicle.append(job)
                current_capacity += job.weight
            else:
                if current_vehicle:
                    vehicles.append(current_vehicle)
                current_vehicle = [job]
                current_capacity = job.weight
        
        if current_vehicle:
            vehicles.append(current_vehicle)
        
        return vehicles

@celery.task
def optimize_partition(partition, vehicles_available):
    """Optimize a single partition of jobs"""
    optimizer = GeneticAlgorithm()
    return optimizer.optimize(partition, vehicles_available)

@celery.task
def aggregate_optimization_results(results):
    """Aggregate results from parallel optimization"""
    aggregated = {
        'routes': [],
        'total_distance': 0,
        'total_duration': 0,
        'vehicles_used': 0
    }
    
    for result in results:
        aggregated['routes'].extend(result['routes'])
        aggregated['total_distance'] += result['total_distance']
        aggregated['total_duration'] += result['total_duration']
        aggregated['vehicles_used'] += result['vehicles_used']
    
    return aggregated
