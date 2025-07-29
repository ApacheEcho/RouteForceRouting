# Routing Module

This module provides route optimization, scoring, and utility functions for RouteForceRouting.

## Key Features

- Route generation and optimization (legacy and modern APIs)
- Deterministic, testable route scoring
- Playbook constraint enforcement
- Utilities for geocoding, distance, and file loading

## Main Files

- `core.py`: Legacy API delegating to modern services
- `route_scorer.py`: Unified, deterministic scoring logic
- `metrics.py`: Scoring API for integration
- `loader.py`: Store data loading from CSV/Excel/Parquet
- `playbook_constraints.py`: Playbook constraint logic
- `utils.py`: Geocoding and address utilities

## Requirements

See `requirements.txt` for dependencies.

## Testing

Unit tests are in `routing/test/`. Run with `pytest` from the project root.
