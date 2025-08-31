"""
Random seed utilities for deterministic runs.

Reads the RFR_SEED environment variable (if set) and seeds common
PRNGs used across the codebase. Safe to call multiple times.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def seed_all(seed: int) -> None:
    """Seed Python's random and, if available, numpy PRNGs.

    Args:
        seed: Integer seed value.
    """
    try:
        import random

        random.seed(seed)
    except Exception as e:
        logger.debug(f"random.seed failed: {e}")

    # Seed numpy if present; ignore if not installed
    try:
        import numpy as np  # type: ignore

        np.random.seed(seed)
    except Exception:
        # numpy may not be installed or may fail to import in minimal envs
        pass


def seed_all_from_env(default: int | None = None) -> int | None:
    """Seed PRNGs from RFR_SEED environment variable if present.

    Args:
        default: Optional fallback seed when env var is not set.

    Returns:
        The seed that was applied, or None if no seeding occurred.
    """
    val = os.getenv("RFR_SEED")
    if val is None and default is None:
        return None

    seed_str = val if val is not None else str(default)
    try:
        seed_int = int(seed_str)
    except Exception:
        logger.warning(
            f"Invalid RFR_SEED value '{seed_str}', expected integer; skipping seeding"
        )
        return None

    seed_all(seed_int)
    logger.info(f"Deterministic seeding enabled (RFR_SEED={seed_int})")
    return seed_int
