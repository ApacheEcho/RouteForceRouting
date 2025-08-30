#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5002}
echo "GET ${BASE_URL}/api/v1/health"
curl -sS "${BASE_URL}/api/v1/health" -H 'Accept: application/json'
echo

