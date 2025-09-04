#!/usr/bin/env python3
"""
Validate that /api/swagger.json and the static openapi.json match in key aspects:
- Both are valid Swagger 2.0 JSON
- Path sets are identical
Exits non-zero on failure.
"""
import json
import os
import sys

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app

def main():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.test_client() as c:
        r = c.get("/api/swagger.json")
        if r.status_code != 200:
            print(f"ERROR: /api/swagger.json -> {r.status_code}", file=sys.stderr)
            sys.exit(1)
        live = r.get_json()
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "openapi.json"))
    if not os.path.exists(static_path):
        print(f"ERROR: static openapi.json not found at {static_path}", file=sys.stderr)
        sys.exit(1)
    with open(static_path) as f:
        static = json.load(f)

    # Basic checks
    for name, spec in (("live", live), ("static", static)):
        if spec.get("swagger") != "2.0":
            print(f"ERROR: {name} spec is not Swagger 2.0", file=sys.stderr)
            sys.exit(1)

    live_paths = set(live.get("paths", {}).keys())
    static_paths = set(static.get("paths", {}).keys())
    missing_in_static = live_paths - static_paths
    missing_in_live = static_paths - live_paths

    ok = True
    if missing_in_static:
        print("ERROR: Paths missing in static openapi.json:")
        for p in sorted(missing_in_static):
            print(f"  - {p}")
        ok = False
    if missing_in_live:
        print("ERROR: Extra paths in static openapi.json (not in live):")
        for p in sorted(missing_in_live):
            print(f"  - {p}")
        ok = False

    if not ok:
        sys.exit(2)

    print(f"OK: Path parity verified. {len(live_paths)} paths")

if __name__ == "__main__":
    main()
