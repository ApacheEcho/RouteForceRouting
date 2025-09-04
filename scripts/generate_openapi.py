#!/usr/bin/env python3
"""
Generate openapi.json by mirroring the live Flasgger spec (/api/swagger.json).
Keeps the static file in sync with the app's routes and docstrings.
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
    env = os.environ.get("FLASK_ENV", "development")
    app = create_app(env)
    with app.test_client() as c:
        resp = c.get("/api/swagger.json")
        if resp.status_code != 200:
            print(f"Error: GET /api/swagger.json -> {resp.status_code}", file=sys.stderr)
            sys.exit(1)
        spec = resp.get_json()
    out_path = os.path.join(os.path.dirname(__file__), "..", "openapi.json")
    out_path = os.path.abspath(out_path)
    with open(out_path, "w") as f:
        json.dump(spec, f, indent=2)
    print(f"Wrote {out_path} with {len(spec.get('paths',{}))} paths")

if __name__ == "__main__":
    main()
