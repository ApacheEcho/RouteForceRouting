---
applyTo: '**'
---

# Memory: RouteForceRouting / Flask Auth Debug

- The /api/v1/logout endpoint is defined in app/routes/api.py under api_bp, but is not being registered in the Flask app during tests.
- The /api/v1/logout route is missing from the printed route list, even after removing a stray YAML block that was breaking parsing after the route definition.
- All other /api/v1/* endpoints from api_bp are present and working.
- The test client is targeting the correct URL, and the blueprint is registered at the root.
- There are no duplicate or conflicting /logout routes in other blueprints.
- The issue is likely due to a silent syntax or import error, or a code path that skips the /logout definition in the test environment.
- Next step: check for any remaining syntax errors, accidental early returns, or import issues in app/routes/api.py after the /logout route.
