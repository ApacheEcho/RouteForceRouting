#!/usr/bin/env python3
"""
Prints the set of required secrets for RouteForce deployments and which method is being used
based on the presence of environment variables in the current shell.
This is a helper for quick setup sanity before configuring GitHub secrets.
"""

import os


RENDER_KEYS = [
    ("RENDER_DEPLOY_HOOK", "Deploy Hook URL (preferred)"),
    ("RENDER_API_KEY", "API key (alternative)"),
    ("RENDER_SERVICE_ID", "Service ID (required with API key)"),
]

APP_KEYS = [
    ("SECRET_KEY", "Flask secret key"),
    ("JWT_SECRET_KEY", "JWT signing key"),
    ("CORS_ORIGINS", "Comma-separated allowed origins"),
    ("SENTRY_DSN", "Sentry DSN (optional)"),
]


def main() -> int:
    print("RouteForce Required Secrets\n============================")
    print("\nRender Deployment:")
    have_hook = bool(os.getenv("RENDER_DEPLOY_HOOK"))
    have_api = bool(os.getenv("RENDER_API_KEY")) and bool(os.getenv("RENDER_SERVICE_ID"))
    method = "Deploy Hook" if have_hook else ("API Key + Service ID" if have_api else "Not configured")
    print(f"- Deployment method: {method}")
    for k, desc in RENDER_KEYS:
        val = os.getenv(k)
        status = "✅ set" if val else "❌ missing"
        print(f"  - {k}: {status} ({desc})")

    print("\nApplication Secrets:")
    for k, desc in APP_KEYS:
        val = os.getenv(k)
        status = "✅ set" if val else "❌ missing"
        print(f"  - {k}: {status} ({desc})")

    print("\nNotes:")
    print("- Prefer RENDER_DEPLOY_HOOK for simplest CI trigger.")
    print("- In production, CORS_ORIGINS must be explicitly set.")
    print("- Set secrets via GitHub Secrets; local env shown here is only for reference.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

