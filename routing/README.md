Routing Engine Guide

Overview

- The routing engine builds efficient visit sequences from a set of stores and constraints. It supports fast heuristics for day-to-day routing and advanced optimizers for exploration and benchmarking. The recommended entry point is `UnifiedRoutingService.generate_route_from_stores(...)`, which normalizes inputs, applies constraints/filters, chooses the requested algorithm, and records metrics.

Algorithms

- Priority: Orders by weighted priority (per chain or category) and name for stability. Good when business priority dominates distance.
- Nearest-Neighbor: Greedy distance-first routing with a priority-aware start. Fast and robust baseline for up to a few hundred stops.
- Genetic: Population-based search (GA) with crossover and mutation. Finds better solutions for complex instances; tunable via population and generations.
- Simulated Annealing: Single-solution stochastic search; useful for escaping local minima with lightweight tuning.
- Multi-Objective: NSGA-II Pareto optimization balancing multiple objectives (distance, time, priority, fuel). Use for trade-off exploration, then pick a compromise route.

Constraints and Filters

- `RouteConstraints` (see `app/services/route_core.py`):
  - `max_stores`: Cap the number of stops; engine preselects by priority, then applies routing.
  - `time_windows`: Map of chain→{start,end} in HH:MM; filters out stores not serviceable at the visit time.
  - `priority_weights`: Map of chain→weight; used by Priority and as the initial pivot for Nearest-Neighbor.
  - `visit_date`: Datetime used to evaluate `time_windows` at request time.

Metrics

- Each run returns processing time, total distance, optimization score (stores/distance), and algorithm name. Advanced optimizers add algorithm-specific metrics (e.g., GA generations, SA schedule parameters, or multi-objective Pareto size/hypervolume).

Python Usage

```python
from app.services.routing_service_unified import UnifiedRoutingService

stores = [
    {"name": "Store A", "lat": 40.71, "lon": -74.00, "chain": "A", "priority": 2},
    {"name": "Store B", "lat": 40.76, "lon": -73.98, "chain": "B", "priority": 1},
]

constraints = {
    "max_stores": 10,
    "priority_weights": {"A": 2.0, "B": 1.0}
}

options = {"algorithm": "nearest_neighbor"}

svc = UnifiedRoutingService()
route = svc.generate_route_from_stores(stores, constraints, algorithm=options["algorithm"], algorithm_params=options)
metrics = svc.get_metrics()
print("Stops:", len(route), "Distance:", metrics.total_distance, "Algo:", metrics.algorithm_used)
```

API Example

- Create an optimized route (supports algorithm selection and params):

```bash
curl -X POST http://localhost:8000/api/v1/routes \
  -H 'Content-Type: application/json' \
  -d '{
    "stores": [
      {"name": "Store A", "lat": 40.71, "lon": -74.00, "priority": 2},
      {"name": "Store B", "lat": 40.76, "lon": -73.98, "priority": 1}
    ],
    "constraints": {"max_stores": 10},
    "options": {
      "algorithm": "genetic",
      "ga_population_size": 50,
      "ga_generations": 100
    }
  }'
```

Advanced Optimizers

- Genetic (`app/optimization/genetic_algorithm.py`): Configure `population_size`, `generations`, `mutation_rate`, `crossover_rate`. Larger populations and more generations improve quality at higher CPU cost.
- Simulated Annealing (`app/optimization/simulated_annealing.py`): Tune `initial_temperature`, `cooling_rate`, `min_temperature`. Good for mid-sized instances with time budgets.
- Multi-Objective (`app/optimization/multi_objective.py`): Choose objectives via `options.mo_objectives` (e.g., `distance,time,priority`). After a run, call `MultiObjectiveOptimizer.get_pareto_front()` (when used directly) to inspect Pareto-optimal alternatives with objective values and crowding distance. The unified service focuses on single-objective flows; use the direct class for Pareto exploration.

Scoring

- `app/services/route_scoring_service.py` computes a weighted score across distance, time, priority, traffic, playbook adherence, and efficiency. Presets (`balanced`, `distance_focused`, etc.) are exposed via the API:
  - `POST /api/route/score` for a single route.
  - `POST /api/route/score/compare` for multiple alternatives.

Tips

- Data: Provide either `lat/lon` or a resolvable `address`. The engine normalizes `lng` to `lon` where needed.
- Geocoding cache: Results are cached to reduce external lookups; repeated runs on the same addresses will be faster.
- Content-Type: Most `/api/*` POST endpoints require `Content-Type: application/json`. Exceptions include `/api/v1/refresh` and `/api/v1/logout`.

