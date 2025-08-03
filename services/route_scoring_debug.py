"""
Route Scoring Debug Diagnostics Module

This module provides functions to output a detailed breakdown of how a route score was calculated.
Intended for developer/AI agent transparency, testing, and frontend integration.
"""

from typing import Dict, Any

def debug_route_score(route_score: Any) -> Dict[str, Any]:
    """
    Given a RouteScore object (from the scoring service), return a detailed breakdown of the score calculation.
    Args:
        route_score: RouteScore object (should have total_score, component_scores, raw_metrics, scoring_metadata)
    Returns:
        dict with per-component breakdown, weights, raw values, weighted contributions, and total formula.
    """
    breakdown = {}
    weights = route_score.scoring_metadata.get("weights_used", {})
    components = route_score.component_scores
    total_score = route_score.total_score
    raw_metrics = route_score.raw_metrics
    formula = []
    weighted_sum = 0.0
    for k, v in components.items():
        weight = weights.get(k, 0)
        contrib = v * weight * 100
        breakdown[k] = {
            "raw_value": v,
            "weight": weight,
            "weighted_contribution": contrib,
            "raw_metric": raw_metrics.get(k)
        }
        formula.append(f"({k}: {v:.3f} × {weight:.2f})")
        weighted_sum += contrib
    return {
        "total_score": total_score,
        "weighted_sum": weighted_sum,
        "components": breakdown,
        "weights": weights,
        "raw_metrics": raw_metrics,
        "scoring_metadata": route_score.scoring_metadata,
        "calculation_time_ms": route_score.calculation_time,
        "formula": " + ".join(formula) + " × 100"
    }

def print_route_score_debug(route_score: Any):
    """
    Print a human-readable debug summary of the route score breakdown.
    """
    debug = debug_route_score(route_score)
    print("\n=== Route Score Debug Breakdown ===")
    print(f"Total Score: {debug['total_score']:.2f}")
    print(f"Weighted Sum: {debug['weighted_sum']:.2f}")
    print(f"Formula: {debug['formula']}")
    print("\nComponent Contributions:")
    for k, v in debug["components"].items():
        print(f"  {k}: raw={v['raw_value']:.3f}, weight={v['weight']:.2f}, contrib={v['weighted_contribution']:.2f}")
    print("\nRaw Metrics:")
    for k, v in debug["raw_metrics"].items():
        print(f"  {k}: {v}")
    print("\nScoring Metadata:")
    for k, v in debug["scoring_metadata"].items():
        print(f"  {k}: {v}")
