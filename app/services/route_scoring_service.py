"""
Route Scoring Service - ML-based and rule-based route scoring system
Provides weighted scoring for routes based on multiple criteria
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ScoreComponent(Enum):
    """Components that contribute to route scoring"""

    DISTANCE = "distance"
    TIME = "time"
    PRIORITY = "priority"
    TRAFFIC = "traffic"
    PLAYBOOK = "playbook"
    EFFICIENCY = "efficiency"
    BALANCE = "balance"


@dataclass
class ScoringWeights:
    """Configurable weights for different scoring components"""

    distance_weight: float = 0.25  # Lower distance = higher score
    time_weight: float = 0.20  # Lower time = higher score
    priority_weight: float = 0.25  # Higher priority = higher score
    traffic_weight: float = 0.15  # Lower traffic = higher score
    playbook_weight: float = 0.10  # Playbook compliance = higher score
    efficiency_weight: float = 0.05  # Route efficiency = higher score

    def __post_init__(self):
        """Ensure weights sum to 1.0"""
        total = (
            self.distance_weight
            + self.time_weight
            + self.priority_weight
            + self.traffic_weight
            + self.playbook_weight
            + self.efficiency_weight
        )
        if abs(total - 1.0) > 0.01:
            logger.warning(
                f"Scoring weights sum to {total:.3f}, not 1.0. Auto-normalizing."
            )
            # Normalize weights
            self.distance_weight /= total
            self.time_weight /= total
            self.priority_weight /= total
            self.traffic_weight /= total
            self.playbook_weight /= total
            self.efficiency_weight /= total


@dataclass
class RouteScore:
    """Comprehensive route score with component breakdown"""

    total_score: float
    component_scores: dict[str, float] = field(default_factory=dict)
    raw_metrics: dict[str, Any] = field(default_factory=dict)
    scoring_metadata: dict[str, Any] = field(default_factory=dict)
    calculation_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "total_score": round(self.total_score, 2),
            "component_scores": {
                k: round(v, 3) for k, v in self.component_scores.items()
            },
            "raw_metrics": self.raw_metrics,
            "metadata": self.scoring_metadata,
            "calculation_time_ms": round(self.calculation_time * 1000, 2),
        }


class RouteScorer:
    """Main route scoring service with configurable weights and algorithms"""

    def __init__(self, weights: ScoringWeights | None = None):
        self.weights = weights or ScoringWeights()
        self.scoring_history = []

    def score_route(
        self, route: list[dict], context: dict | None = None
    ) -> RouteScore:
        """
        Calculate comprehensive score for a route

        Args:
            route: List of stores in route order
            context: Optional context (playbook, traffic data, etc.)

        Returns:
            RouteScore with total score and component breakdown
        """
        start_time = time.time()
        context = context or {}

        try:
            # Calculate component scores
            distance_score = self._calculate_distance_score(route)
            time_score = self._calculate_time_score(route, context)
            priority_score = self._calculate_priority_score(route)
            traffic_score = self._calculate_traffic_score(route, context)
            playbook_score = self._calculate_playbook_score(route, context)
            efficiency_score = self._calculate_efficiency_score(route)

            # Weighted total score (0-100 scale)
            total_score = (
                distance_score * self.weights.distance_weight
                + time_score * self.weights.time_weight
                + priority_score * self.weights.priority_weight
                + traffic_score * self.weights.traffic_weight
                + playbook_score * self.weights.playbook_weight
                + efficiency_score * self.weights.efficiency_weight
            ) * 100

            # Create comprehensive result
            route_score = RouteScore(
                total_score=total_score,
                component_scores={
                    ScoreComponent.DISTANCE.value: distance_score,
                    ScoreComponent.TIME.value: time_score,
                    ScoreComponent.PRIORITY.value: priority_score,
                    ScoreComponent.TRAFFIC.value: traffic_score,
                    ScoreComponent.PLAYBOOK.value: playbook_score,
                    ScoreComponent.EFFICIENCY.value: efficiency_score,
                },
                raw_metrics=self._extract_raw_metrics(route, context),
                scoring_metadata={
                    "route_length": len(route),
                    "weights_used": {
                        "distance": self.weights.distance_weight,
                        "time": self.weights.time_weight,
                        "priority": self.weights.priority_weight,
                        "traffic": self.weights.traffic_weight,
                        "playbook": self.weights.playbook_weight,
                        "efficiency": self.weights.efficiency_weight,
                    },
                    "algorithm_version": "1.0",
                },
                calculation_time=time.time() - start_time,
            )

            # Store in history for analysis
            self.scoring_history.append(
                {
                    "timestamp": time.time(),
                    "route_id": context.get("route_id", f"route_{int(time.time())}"),
                    "score": route_score,
                }
            )

            return route_score

        except Exception as e:
            logger.error(f"Error calculating route score: {e}")
            return RouteScore(
                total_score=0.0,
                scoring_metadata={"error": str(e)},
                calculation_time=time.time() - start_time,
            )

    def _calculate_distance_score(self, route: list[dict]) -> float:
        """Calculate score based on total route distance (lower = better)"""
        if len(route) < 2:
            return 1.0

        try:
            from app.services.distance_service import \
                create_distance_calculator

            calculator = create_distance_calculator()

            total_distance = 0.0
            for i in range(len(route) - 1):
                distance = calculator.calculate_store_distance(route[i], route[i + 1])
                total_distance += distance

            # Normalize score (assume 200km is baseline for 0.5 score)
            baseline_distance = 200.0
            score = max(0.0, min(1.0, baseline_distance / max(total_distance, 1.0)))
            return score

        except Exception as e:
            logger.warning(f"Error calculating distance score: {e}")
            return 0.5  # Neutral score on error

    def _calculate_time_score(self, route: list[dict], context: dict) -> float:
        """Calculate score based on estimated travel time (lower = better)"""
        if len(route) < 2:
            return 1.0

        try:
            # Estimate time based on distance (assume average 60 km/h)
            from app.services.distance_service import \
                create_distance_calculator

            calculator = create_distance_calculator()

            total_time = 0.0
            for i in range(len(route) - 1):
                distance = calculator.calculate_store_distance(route[i], route[i + 1])
                # Add travel time + service time per store
                travel_time = distance / 60.0  # hours at 60 km/h
                service_time = 0.5  # 30 minutes per store
                total_time += travel_time + service_time

            # Normalize score (assume 8 hours is baseline for 0.5 score)
            baseline_time = 8.0
            score = max(0.0, min(1.0, baseline_time / max(total_time, 1.0)))
            return score

        except Exception as e:
            logger.warning(f"Error calculating time score: {e}")
            return 0.5

    def _calculate_priority_score(self, route: list[dict]) -> float:
        """Calculate score based on store priorities (higher priority = better)"""
        if not route:
            return 0.0

        try:
            total_priority = 0.0
            max_possible = 0.0

            for store in route:
                priority = store.get("priority", 5)  # Default to medium priority
                weight = store.get("weight", 1.0)  # Store weight multiplier

                total_priority += priority * weight
                max_possible += 10 * weight  # Assume max priority is 10

            score = total_priority / max(max_possible, 1.0)
            return min(1.0, score)

        except Exception as e:
            logger.warning(f"Error calculating priority score: {e}")
            return 0.5

    def _calculate_traffic_score(self, route: list[dict], context: dict) -> float:
        """Calculate score based on traffic conditions (lower traffic = better)"""
        try:
            # Check if traffic data is available in context
            traffic_data = context.get("traffic_data", {})

            if not traffic_data:
                return 0.7  # Neutral-good score when no traffic data

            total_delay = traffic_data.get("total_delay", 0)
            total_time = traffic_data.get("total_time", 1)

            # Score based on traffic delay ratio
            delay_ratio = total_delay / max(total_time, 1)
            score = max(0.0, 1.0 - delay_ratio)

            return score

        except Exception as e:
            logger.warning(f"Error calculating traffic score: {e}")
            return 0.7

    def _calculate_playbook_score(self, route: list[dict], context: dict) -> float:
        """Calculate score based on playbook compliance"""
        try:
            playbook = context.get("playbook", {})

            if not playbook:
                return 0.8  # Good score when no playbook constraints

            compliance_score = 0.0
            total_rules = 0

            # Check various playbook rules
            rules = playbook.get("rules", [])
            for rule in rules:
                total_rules += 1
                if self._check_rule_compliance(route, rule):
                    compliance_score += 1.0

            if total_rules == 0:
                return 0.8

            return compliance_score / total_rules

        except Exception as e:
            logger.warning(f"Error calculating playbook score: {e}")
            return 0.8

    def _calculate_efficiency_score(self, route: list[dict]) -> float:
        """Calculate score based on route efficiency (geometric optimization)"""
        if len(route) < 3:
            return 1.0

        try:
            # Calculate efficiency based on how close the route is to optimal
            # Compare actual distance to minimum spanning tree distance
            from app.services.distance_service import \
                create_distance_calculator

            calculator = create_distance_calculator()

            # Calculate actual route distance
            actual_distance = 0.0
            for i in range(len(route) - 1):
                actual_distance += calculator.calculate_store_distance(
                    route[i], route[i + 1]
                )

            # Estimate optimal distance (simplified MST approximation)
            optimal_distance = self._estimate_optimal_distance(route, calculator)

            if optimal_distance <= 0:
                return 0.5

            efficiency = optimal_distance / max(actual_distance, 1.0)
            return min(1.0, efficiency)

        except Exception as e:
            logger.warning(f"Error calculating efficiency score: {e}")
            return 0.5

    def _estimate_optimal_distance(self, route: list[dict], calculator) -> float:
        """Estimate optimal route distance using simplified MST"""
        if len(route) < 2:
            return 0.0

        # Simple heuristic: average distance between nearest neighbors
        total_distance = 0.0
        for i, store in enumerate(route):
            min_distance = float("inf")
            for j, other in enumerate(route):
                if i != j:
                    distance = calculator.calculate_store_distance(store, other)
                    min_distance = min(min_distance, distance)
            if min_distance != float("inf"):
                total_distance += min_distance

        return total_distance * 0.8  # MST is typically ~80% of sum of nearest neighbors

    def _check_rule_compliance(self, route: list[dict], rule: dict) -> bool:
        """Check if route complies with a specific playbook rule"""
        rule_type = rule.get("type", "")

        if rule_type == "max_stores":
            return len(route) <= rule.get("value", 999)
        elif rule_type == "required_chain":
            required_chain = rule.get("value", "")
            return any(
                store.get("chain", "").lower() == required_chain.lower()
                for store in route
            )
        elif rule_type == "avoid_chain":
            avoided_chain = rule.get("value", "")
            return not any(
                store.get("chain", "").lower() == avoided_chain.lower()
                for store in route
            )
        elif rule_type == "priority_threshold":
            threshold = rule.get("value", 0)
            return all(store.get("priority", 5) >= threshold for store in route)

        return True  # Unknown rules default to compliant

    def _extract_raw_metrics(self, route: list[dict], context: dict) -> dict[str, Any]:
        """Extract raw metrics for detailed analysis"""
        try:
            from app.services.distance_service import \
                create_distance_calculator

            calculator = create_distance_calculator()

            total_distance = 0.0
            for i in range(len(route) - 1):
                total_distance += calculator.calculate_store_distance(
                    route[i], route[i + 1]
                )

            priorities = [store.get("priority", 5) for store in route]

            return {
                "total_distance_km": round(total_distance, 2),
                "store_count": len(route),
                "average_priority": round(sum(priorities) / max(len(priorities), 1), 2),
                "min_priority": min(priorities) if priorities else 0,
                "max_priority": max(priorities) if priorities else 0,
                "has_traffic_data": "traffic_data" in context,
                "has_playbook": "playbook" in context and bool(context["playbook"]),
            }

        except Exception as e:
            logger.warning(f"Error extracting raw metrics: {e}")
            return {"error": str(e)}

    def compare_routes(
        self, routes: list[list[dict]], context: dict | None = None
    ) -> dict[str, Any]:
        """Compare multiple routes and return detailed comparison"""
        if not routes:
            return {"error": "No routes provided"}

        scores = []
        for i, route in enumerate(routes):
            route_context = context.copy() if context else {}
            route_context["route_id"] = f"comparison_route_{i}"
            score = self.score_route(route, route_context)
            scores.append(score)

        # Find best route
        best_idx = max(range(len(scores)), key=lambda i: scores[i].total_score)

        return {
            "route_count": len(routes),
            "scores": [score.to_dict() for score in scores],
            "best_route_index": best_idx,
            "best_score": scores[best_idx].total_score,
            "score_range": {
                "min": min(score.total_score for score in scores),
                "max": max(score.total_score for score in scores),
                "average": sum(score.total_score for score in scores) / len(scores),
            },
        }

    def get_scoring_history(self, limit: int = 10) -> list[dict]:
        """Get recent scoring history for analysis"""
        return self.scoring_history[-limit:] if self.scoring_history else []

    def update_weights(self, new_weights: ScoringWeights) -> None:
        """Update scoring weights"""
        self.weights = new_weights
        logger.info("Updated route scoring weights")


# Factory function for easy instantiation
def create_route_scorer(weights: ScoringWeights | None = None) -> RouteScorer:
    """Create a route scorer with optional custom weights"""
    return RouteScorer(weights)


# Preset weight configurations
PRESET_WEIGHTS = {
    "balanced": ScoringWeights(),
    "distance_focused": ScoringWeights(
        distance_weight=0.4,
        time_weight=0.3,
        priority_weight=0.2,
        traffic_weight=0.05,
        playbook_weight=0.03,
        efficiency_weight=0.02,
    ),
    "priority_focused": ScoringWeights(
        priority_weight=0.4,
        distance_weight=0.2,
        time_weight=0.2,
        traffic_weight=0.1,
        playbook_weight=0.07,
        efficiency_weight=0.03,
    ),
    "traffic_aware": ScoringWeights(
        traffic_weight=0.3,
        time_weight=0.25,
        distance_weight=0.25,
        priority_weight=0.15,
        playbook_weight=0.03,
        efficiency_weight=0.02,
    ),
    "playbook_strict": ScoringWeights(
        playbook_weight=0.3,
        priority_weight=0.25,
        distance_weight=0.2,
        time_weight=0.15,
        traffic_weight=0.07,
        efficiency_weight=0.03,
    ),
}


def create_route_scorer_preset(preset: str = "balanced") -> RouteScorer:
    """Create a route scorer with preset weight configuration"""
    weights = PRESET_WEIGHTS.get(preset, PRESET_WEIGHTS["balanced"])
    return RouteScorer(weights)
