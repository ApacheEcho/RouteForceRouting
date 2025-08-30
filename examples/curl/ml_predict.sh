#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${BASE_URL:-http://localhost:5002}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${SCRIPT_DIR}/../payloads"
BODY="${PAYLOAD_DIR}/ml_predict.json"

echo "POST ${BASE_URL}/api/v1/ml/predict"
curl -sS -X POST "${BASE_URL}/api/v1/ml/predict" \
  -H 'Content-Type: application/json' \
  --data-binary "@${BODY}"
echo

