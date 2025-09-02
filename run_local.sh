#!/usr/bin/env bash
set -euo pipefail

# Start backend in background
echo 'Starting backend...'
python3 -m venv .venv || true
source .venv/bin/activate
pip install -r backend/requirements.txt
python3 backend/app.py &
BACKEND_PID=$!

# Start frontend
echo 'Starting frontend...'
npm install --no-audit
npm start

# On exit, kill backend
trap "echo 'Stopping backend'; kill $BACKEND_PID" EXIT
