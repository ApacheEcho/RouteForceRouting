"""
Test file to debug routing service import issue
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from flask import current_app
from geopy.distance import geodesic

# Import optimization algorithms
from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
from app.optimization.multi_objective import (
    MultiObjectiveConfig,
    MultiObjectiveOptimizer,
)
from app.optimization.simulated_annealing import (
    SimulatedAnnealingConfig,
    SimulatedAnnealingOptimizer,
)

# Import traffic service
from app.services.traffic_service import TrafficConfig, TrafficService
from routing.core import generate_route as core_generate_route

logger = logging.getLogger(__name__)

print("All imports successful")


# Test the class definition
class TestRoutingService:
    def __init__(self):
        print("TestRoutingService initialized")


print("Class defined successfully")
