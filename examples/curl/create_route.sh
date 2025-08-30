#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5002}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${SCRIPT_DIR}/../payloads"
BODY="${PAYLOAD_DIR}/create_route.json"

echo "POST ${BASE_URL}/api/v1/routes"
curl -sS -X POST "${BASE_URL}/api/v1/routes" \
  -H 'Content-Type: application/json' \
  --data-binary "@${BODY}"
echo

