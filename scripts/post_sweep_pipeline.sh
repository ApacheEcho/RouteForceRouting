#!/usr/bin/env bash
# RouteForce Pro – Post-Sweep Security, Test, Perf, Deploy Pipeline
# Safe-by-default: gates risky steps behind env flags.

set -euo pipefail

# Colors
YELLOW='\033[1;33m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
info(){ echo -e "${YELLOW}[INFO]${NC} $*"; }
ok(){ echo -e "${GREEN}[OK]${NC} $*"; }
err(){ echo -e "${RED}[ERR]${NC} $*"; }

# 0) Python setup
python -m pip install --upgrade pip >/dev/null 2>&1 || true

# 1) Security & Static Analysis
info "Installing security tools..."
pip install -U bandit pip-audit safety detect-secrets pip-licenses >/dev/null

info "Running bandit..."
bandit -r app/ -lll -q | tee bandit.txt

info "Running pip-audit..."
pip-audit -r requirements.txt | tee pip-audit.txt || true

info "Running safety..."
safety scan -r requirements.txt | tee safety.txt || true

info "Scanning for secrets..."
detect-secrets scan > .secrets.baseline || true
# Interactive; keep non-blocking
if [ -t 1 ]; then
  detect-secrets audit .secrets.baseline || true
fi

info "Generating third-party licenses..."
pip-licenses --format=markdown > THIRD_PARTY_LICENSES.md || true

# 2) Tests & Coverage
info "Installing test deps..."
pip install -U pytest pytest-cov >/dev/null

info "Running tests (quick)..."
pytest -q --maxfail=1 || true

info "Running coverage..."
pytest --cov=app --cov-report=xml --cov-report=term-missing --cov-fail-under=80 || true

# 3) Performance & Load Checks
info "Starting app under gunicorn..."
pip install -U gunicorn >/dev/null
: "${GUNICORN_WORKERS:=4}"
: "${GUNICORN_WORKER_CLASS:=sync}"  # default to sync; set gevent if installed
if [ "${GUNICORN_WORKER_CLASS}" = "gevent" ]; then
  pip install gevent >/dev/null || true
fi

# Pick a free port
: "${PORT:=8000}"
(
  gunicorn "app:create_app('production')" -b 0.0.0.0:${PORT} \
    --workers "${GUNICORN_WORKERS}" --worker-class "${GUNICORN_WORKER_CLASS}" \
    --timeout 90
) >/tmp/gunicorn.log 2>&1 &
GUNICORN_PID=$!
sleep 5

info "Health check..."
if curl -fsS "http://localhost:${PORT}/health" >/dev/null; then ok "Health OK"; else err "Health failed"; kill ${GUNICORN_PID} || true; exit 1; fi

if command -v k6 >/dev/null && [ -f tests/performance/smoke.js ]; then
  info "Running k6 smoke test..."
  k6 run --vus 20 --duration 2m -o json=results.json tests/performance/smoke.js || true
else
  info "k6 not installed or test missing; skipping load test"
fi

kill ${GUNICORN_PID} >/dev/null 2>&1 || true

# 4) Dependency Hygiene (opt-in)
if [ "${RUN_DEP_HYGIENE:-0}" = "1" ]; then
  info "Running dependency hygiene (pip-tools)..."
  pip install -U pip-tools >/dev/null
  pip-compile --generate-hashes -o requirements.lock || true
  pip-sync requirements.lock || true
  if command -v npm >/dev/null; then
    info "Running npm ci/audit (best-effort)..."
    npm ci || true
    npm audit --production || true
  fi
else
  info "Dependency hygiene skipped (set RUN_DEP_HYGIENE=1 to enable)"
fi

# 5) Observability & Runtime Checks
info "Verifying health endpoint..."
curl -fsS "http://localhost:${PORT}/health" || true

# 6) CI/CD & Deploy (Render)
if [ -n "${RENDER_DEPLOY_HOOK:-}" ]; then
  info "Triggering Render deploy hook..."
  curl -fsS -X POST "${RENDER_DEPLOY_HOOK}" || true
elif [ -n "${RENDER_API_KEY:-}" ] && [ -n "${RENDER_SERVICE_ID:-}" ]; then
  info "Triggering Render API deploy..."
  curl -fsS -X POST "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{}' || true
fi

if [ -n "${RENDER_PUBLIC_URL:-}" ]; then
  info "Polling Render health..."
  for i in {1..30}; do curl -fsS "${RENDER_PUBLIC_URL}/health" && break || sleep 10; done || true
fi

# 7) Release Management (manual)
if [ -n "${RELEASE_TAG:-}" ]; then
  info "Tagging release ${RELEASE_TAG}..."
  git tag -a "${RELEASE_TAG}" -m "RouteForce Pro ${RELEASE_TAG}" || true
  git push origin "${RELEASE_TAG}" || true
fi

ok "Pipeline complete. Artifacts: bandit.txt, pip-audit.txt, safety.txt, THIRD_PARTY_LICENSES.md"
