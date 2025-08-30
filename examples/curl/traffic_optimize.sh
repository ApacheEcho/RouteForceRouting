#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5002}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${SCRIPT_DIR}/../payloads"
BODY="${PAYLOAD_DIR}/traffic_optimize.json"

echo "POST ${BASE_URL}/api/traffic/optimize"
curl -sS -X POST "${BASE_URL}/api/traffic/optimize" \
  -H 'Content-Type: application/json' \
  --data-binary "@${BODY}"
echo

