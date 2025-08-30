#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${1:-http://127.0.0.1:8000}
METRICS_TOKEN=${2:-}
echo "🔎 Smoke testing ${BASE_URL}"
curl -fsS "${BASE_URL}/health" >/dev/null && echo "✅ /health"
HDR=()
if [ -n "$METRICS_TOKEN" ]; then HDR=( -H "X-Metrics-Token: ${METRICS_TOKEN}" ); fi
curl -fsS "${HDR[@]}" "${BASE_URL}/metrics" >/dev/null && echo "✅ /metrics"
curl -fsS "${BASE_URL}/metrics/summary" >/dev/null && echo "✅ /metrics/summary"
curl -fsS "${BASE_URL}/metrics/health" >/dev/null && echo "✅ /metrics/health"
echo "🎉 Smoke tests passed"
