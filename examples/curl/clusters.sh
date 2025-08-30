#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5002}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${SCRIPT_DIR}/../payloads"
BODY="${PAYLOAD_DIR}/clusters.json"

echo "POST ${BASE_URL}/api/v1/clusters"
curl -sS -X POST "${BASE_URL}/api/v1/clusters" \
  -H 'Content-Type: application/json' \
  --data-binary "@${BODY}"
echo

