# routing/route_analysis.py

from typing import List, Dict, Optional
try:
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    import math

    def haversine(coord1, coord2):
        # Approximate radius of earth in miles
        R = 3958.8
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi/2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2.0)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

def calculate_total_distance(route: List[Dict], fallback: str = 'haversine') -> Dict:
    """Returns total distance and breakdown of distances between stops."""
    total_distance = 0.0
    legs = []
    for i in range(len(route) - 1):
        coord1 = (route[i]['lat'], route[i]['lon'])
        coord2 = (route[i + 1]['lat'], route[i + 1]['lon'])
        if GEOPY_AVAILABLE:
            dist = geodesic(coord1, coord2).miles
        else:
            dist = haversine(coord1, coord2)
        total_distance += dist
        legs.append({
            "from": route[i]['name'],
            "to": route[i+1]['name'],
            "miles": dist
        })
    return {
        "total_miles": total_distance,
        "legs": legs
    }

def detect_backtracking(route: List[Dict], tolerance_meters: int = 50) -> Dict:
    """Detects if any store is revisited in the route."""
    seen = {}
    backtracks = []
    for idx, stop in enumerate(route):
        store_id = stop.get("id") or stop.get("name")
        if store_id in seen:
            backtracks.append({
                "store": store_id,
                "first_seen": seen[store_id],
                "revisited_at": idx
            })
        else:
            seen[store_id] = idx
    return {
        "backtracking_detected": len(backtracks) > 0,
        "events": backtracks
    }

def route_density_score(route: List[Dict], travel_time_minutes: Optional[float] = None, adjust_for_city_density: bool = False) -> float:
    """Computes stop density per minute, with optional city adjustment."""
    stop_count = len(route)
    if not travel_time_minutes:
        travel_time_minutes = stop_count * 10  # Assume avg 10 mins between stops
    density = stop_count / travel_time_minutes
    if adjust_for_city_density:
        # Placeholder for future population density logic
        density *= 1.1  # Dummy boost factor
    return density
#### 🚧 Final Engineering Tasks for RouteForcePro

# 1. Scoring Engine
- Create `routing/route_scorer.py` with:
  - `score_efficiency(route)` → composite score from distance, backtracking, density
  - `apply_playbook_constraints(route, playbook)` → returns bool pass/fail + reason

# 2. Key Account Weighting
- Add `priority_weighting(route, key_accounts: List[str])` to `route_scorer.py`
  - Increases score for priority chains
  - Uses `route[i]['chain']` or `route[i]['id']`

# 3. Traffic Simulation
- Create `routing/traffic_simulator.py`
  - `simulate_travel_time(route)` → adds delay values to each leg
  - Optional `weekday='Monday'` param for variation

# 4. Playbook Editor GUI
- Add `templates/playbook_editor.html`:
  - HTMX form with:
    - Chain name input
    - Day/time restrictions (select + checkbox)
    - Button to save playbook JSON

# 5. Store Input Module
- Add to `store_input.py`:
  - `parse_uploaded_csv(file)` → returns validated store dicts
  - `detect_duplicates(stores)` → flags based on lat/lon proximity

# 6. Route Summary Export
- Create `export/route_summary.py`
  - `generate_google_maps_link(route)` → returns shareable link
  - `export_as_pdf(route)` → saves to `/exports`

# 7. Test Regression Safety
- Hook into test runner to:
  - Save snapshots of key metrics to `logs/test_snapshots/`
  - Alert if `score_efficiency()` delta exceeds ±10%

# 8. Deployment Polishing
- Add `render_deploy.sh`:
  - Deploy to Render with env vars
  - Enables staging flag `RFP_ENV=staging`