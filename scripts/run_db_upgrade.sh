#!/usr/bin/env bash
set -euo pipefail

echo "📦 Applying database migrations (flask db upgrade)"

# Ensure we run from the repo root in Docker/Render
cd "$(dirname "$0")/.."

# Configure Flask to use the WSGI app which already selects config from FLASK_ENV
export FLASK_APP=wsgi.py
export FLASK_ENV=${FLASK_ENV:-production}

# Make sure PATH includes venv if present
if [ -d "/opt/venv/bin" ]; then
  export PATH="/opt/venv/bin:$PATH"
fi

python -m flask db upgrade

echo "✅ Database migrations applied"

