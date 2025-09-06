#!/usr/bin/env bash
set -euo pipefail

# Simple post-deploy smoke test.
# Usage: ./scripts/smoke_post_deploy.sh https://app.routeforcepro.com [metrics_token]
# Note: App defaults to port 8000 in production if PORT is not set.
#       Adjust BASE_URL accordingly or set PORT explicitly in your environment.

BASE_URL=${1:-http://127.0.0.1:8000}
METRICS_TOKEN=${2:-}

echo "🔎 Smoke testing ${BASE_URL}"

fail=0

check() {
  local name="$1"; shift
  local cmd=("$@")
  if output=$("${cmd[@]}" 2>&1); then
    echo "✅ ${name}"
  else
    echo "❌ ${name}: ${output}" >&2
    fail=1
  fi
}

# Health endpoint
check "/health" curl -fsS "${BASE_URL}/health"

# Metrics endpoints
if [ -n "$METRICS_TOKEN" ]; then
  HDR=( -H "X-Metrics-Token: ${METRICS_TOKEN}" )
else
  HDR=()
fi

check "/metrics (prometheus)" curl -fsS "${HDR[@]}" "${BASE_URL}/metrics"
check "/metrics/summary" curl -fsS "${HDR[@]}" "${BASE_URL}/metrics/summary"
check "/metrics/health" curl -fsS "${BASE_URL}/metrics/health"

if [ "$fail" -eq 0 ]; then
  echo "🎉 Smoke tests passed"
else
  echo "🚨 Smoke tests failed" >&2
  exit 1
fi
