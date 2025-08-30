import os
from typing import List, Dict, Any

import pytest


def _make_stores(n: int = 8) -> List[Dict[str, Any]]:
    # Simple square around a center point
    base_lat, base_lng = 37.7749, -122.4194
    rng = [(0.01, 0.02), (-0.01, -0.02), (0.015, -0.005), (-0.02, 0.01)]
    out: List[Dict[str, Any]] = []
    for i in range(n):
        dx, dy = rng[i % len(rng)]
        out.append(
            {
                "id": i + 1,
                "name": f"S{i+1}",
                "address": f"{100+i} Test St",
                "latitude": round(base_lat + dx * (i + 1) / n, 6),
                "longitude": round(base_lng + dy * (i + 1) / n, 6),
            }
        )
    return out


@pytest.mark.parametrize("seed", ["123", "999"])
def test_sa_deterministic(monkeypatch: pytest.MonkeyPatch, seed: str):
    try:
        from app.optimization.simulated_annealing import (
            SimulatedAnnealingOptimizer,
            SimulatedAnnealingConfig,
        )
    except Exception as e:
        pytest.skip(f"SA module unavailable: {e}")

    stores = _make_stores(10)
    cfg = SimulatedAnnealingConfig(iterations_per_temp=20, max_iterations=500)
    sa = SimulatedAnnealingOptimizer(cfg)

    monkeypatch.setenv("RFR_SEED", seed)
    route1, metrics1 = sa.optimize(stores)

    # Second run with same seed should be identical
    monkeypatch.setenv("RFR_SEED", seed)
    route2, metrics2 = sa.optimize(stores)

    ids1 = [s.get("id") for s in route1]
    ids2 = [s.get("id") for s in route2]

    assert ids1 == ids2, "SA routes should be identical with same seed"
    assert pytest.approx(metrics1.get("final_distance", 0), rel=0, abs=1e-9) == metrics2.get(
        "final_distance", 0
    )


@pytest.mark.parametrize("seed", ["42"])
def test_ga_deterministic(monkeypatch: pytest.MonkeyPatch, seed: str):
    try:
        from app.optimization.genetic_algorithm import GeneticAlgorithm, GeneticConfig
    except Exception as e:
        pytest.skip(f"GA module unavailable: {e}")

    stores = _make_stores(12)
    cfg = GeneticConfig(population_size=40, generations=120, mutation_rate=0.05)
    ga = GeneticAlgorithm(cfg)

    monkeypatch.setenv("RFR_SEED", seed)
    route1, metrics1 = ga.optimize(stores)

    # Second run with same seed should be identical
    monkeypatch.setenv("RFR_SEED", seed)
    route2, metrics2 = ga.optimize(stores)

    ids1 = [s.get("id") for s in route1]
    ids2 = [s.get("id") for s in route2]

    assert ids1 == ids2, "GA routes should be identical with same seed"
    assert pytest.approx(metrics1.get("final_distance", 0), rel=0, abs=1e-9) == metrics2.get(
        "final_distance", 0
    )

