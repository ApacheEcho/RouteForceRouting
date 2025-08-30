#!/usr/bin/env python3
"""
Post-deploy smoke test for metrics endpoints.

Usage:
  BASE_URL=http://your-host:5000 METRICS_TOKEN=optional-token python3 smoke_metrics.py
"""

import os
import sys
import time
import requests


def get(url: str, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.status_code, r.headers.get("Content-Type", ""), r.text[:300]
    except Exception as e:
        return None, None, str(e)


def main():
    base = os.getenv("BASE_URL", os.getenv("METRICS_BASE_URL", "http://localhost:5000"))
    token = os.getenv("METRICS_TOKEN", "")
    headers = {"X-Metrics-Token": token} if token else {}

    print(f"🔎 Hitting metrics on {base}")

    # /metrics (Prometheus text)
    status, ctype, body = get(f"{base}/metrics", headers=headers)
    print(f"/metrics -> {status} ({ctype})")
    if status == 401 and token:
        print("  ⚠️  Received 401 with token header; trying query param…")
        status, ctype, body = get(f"{base}/metrics?token={token}")
        print(f"/metrics?token=*** -> {status} ({ctype})")

    # /metrics/summary (JSON)
    status, ctype, body = get(f"{base}/metrics/summary", headers=headers)
    print(f"/metrics/summary -> {status} ({ctype})")

    # /metrics/health (JSON, exempt)
    status, ctype, body = get(f"{base}/metrics/health")
    print(f"/metrics/health -> {status} ({ctype})")

    # Basic signal
    ok = status in (200, 204)
    print("✅ Metrics smoke completed" if ok else "❌ Metrics smoke had errors")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

