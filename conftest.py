"""
Test configuration for RouteForce Routing

Simplified configuration without retry logic that was causing issues.
"""

import pytest
import logging
import os
import sys

# Set up basic logging
log_dir = "logs/2025-07-XX/"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "test.log"), 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
