#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export FLASK_APP=wsgi.py
export FLASK_ENV=${FLASK_ENV:-production}
if command -v flask >/dev/null 2>&1; then
  flask db upgrade
else
  python -m flask db upgrade
fi
echo "✅ DB migrations applied"
