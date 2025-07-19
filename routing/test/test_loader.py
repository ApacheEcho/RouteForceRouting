import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from routing.loader import load_stores
from pathlib import Path

SAMPLE_XLSX = Path(__file__).parent.parent / "sample_stores.xlsx"

def test_loads_stores_successfully():
    stores = load_stores(str(SAMPLE_XLSX))
    assert isinstance(stores, list)
    assert len(stores) > 0
    for store in stores:
        assert 'name' in store and store['name']
        assert 'address' in store and store['address']