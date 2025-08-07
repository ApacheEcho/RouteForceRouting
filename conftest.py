"""
Test configuration for RouteForce Routing

Simplified configuration without retry logic that was causing issues.
"""

import pytest
import logging
import os

# Set up basic logging
log_dir = "logs/2025-07-XX/"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "test.log"), 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
