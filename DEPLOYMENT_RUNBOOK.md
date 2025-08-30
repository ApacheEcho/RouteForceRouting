# RouteForce Deployment Runbook

This runbook provides exact, copy-paste steps to deploy RouteForce to production using either Render (recommended) or a VPS (NGINX + Gunicorn + PostgreSQL).

## Prerequisites
- DNS: `app.routeforcepro.com` (or your domain) pointing to your platform.
- GitHub repository with Actions enabled.
- Secrets prepared (see each method below).

## 1) Render Deployment (Recommended)

Render deploy is fully wired via `.github/workflows/deploy.yml` and `render.yaml`.

1. In GitHub repo Settings → Secrets and variables → Actions, add:
   - `RENDER_DEPLOY_HOOK`: Render Deploy Hook URL for your web service
   - Optional alternative: `RENDER_API_KEY` and `RENDER_SERVICE_ID`
   - App secrets: `SECRET_KEY`, `JWT_SECRET_KEY`, `CORS_ORIGINS`, optional `SENTRY_DSN`
   
   How to get these from Render:
   - Deploy Hook: Web Service → Settings → Deploy hooks → Create hook → Copy URL
   - Service ID: Web Service URL includes `srv-XXXXXXXX` (also under Settings → General)
   - API Key: Account → API Keys → Create API Key
2. Push to `main` (or trigger the workflow manually). The workflow:
   - Installs Python deps and runs light tests
   - Builds optional frontends (non-blocking)
   - Triggers a Render deploy (hook or API)
   - Runs DB migrations via `preDeployCommand` (scripts/run_db_upgrade.sh)
3. In Render dashboard, confirm the deploy progresses and health check `/health` returns 200.

Verification:
- Open `https://<your-render-domain-or-custom-domain>/health` → expect `{ status: "healthy" }`.
- Check `/metrics` responds 200. If `METRICS_TOKEN` is set, include header `X-Metrics-Token`.
- Optional: set GitHub Secret `HEALTHCHECK_URL=https://<your-domain>/health` so CI polls readiness and reports to the summary.
- Optional: set GitHub Secret `METRICS_URL=https://<your-domain>/metrics` so CI also validates metrics (uses `X-Metrics-Token` if set).

## 2) VPS Deployment (NGINX + Gunicorn)

Run these steps on your Ubuntu/Debian server as a non-root `deploy` user with sudo rights.

1. Preflight checks locally (optional):
   - `python3 scripts/preflight_deploy_check.py` → ensure all checks pass.
2. Server setup:
   - `scp -r . deploy@your-server:/home/deploy/routeforce`
   - `ssh deploy@your-server`
3. PostgreSQL:
   - Install: `sudo apt update && sudo apt install -y postgresql postgresql-contrib`
   - Create DB/user: follow SQL from `scripts/setup_postgresql.sh`
4. Python app:
   - `cd /home/deploy/routeforce && python3 -m venv venv && source venv/bin/activate`
   - `pip install --upgrade pip && pip install -r requirements.txt`
   - `cp .env.production.template .env.production` and fill: `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`
   - Set `AUTO_COMMIT_ENABLED=false` to disable background git activity on servers
   - Run migrations (preferred):
     - `export FLASK_APP=wsgi.py FLASK_ENV=production`
     - `flask db upgrade`
   - (Fallback for first-time setups only): `python -c "from app import create_app; from app.models.database import db; a=create_app('production'); from flask import current_app;\nwith a.app_context(): db.create_all(); print('DB OK')"`
5. NGINX + SSL:
   - `sudo apt install -y nginx certbot python3-certbot-nginx`
   - `sudo cp nginx/routeforce.conf /etc/nginx/sites-available/routeforce`
   - `sudo ln -sf /etc/nginx/sites-available/routeforce /etc/nginx/sites-enabled/`
   - `sudo nginx -t && sudo systemctl reload nginx`
   - `sudo certbot --nginx -d app.routeforcepro.com` (replace domain as needed)
   - Optional: enable IP allowlist for `/metrics` in `nginx/routeforce.conf`
6. Systemd service:
   - `sudo cp scripts/routeforce.service /etc/systemd/system/` (includes `AUTO_COMMIT_ENABLED=false`)
   - `sudo systemctl daemon-reload && sudo systemctl enable routeforce && sudo systemctl start routeforce`
   - `sudo systemctl status routeforce` (expect running)

Verification:
- `curl -fsS https://app.routeforcepro.com/health` → expect healthy with 200.
- `sudo journalctl -u routeforce -f` → ensure no startup errors.
- Optional: run `scripts/smoke_post_deploy.sh https://app.routeforcepro.com <METRICS_TOKEN>`

## Troubleshooting
- Health failures: inspect `journalctl -u routeforce -f` and `/var/log/nginx/error.log`.
- 502 from NGINX: confirm Gunicorn listens on 127.0.0.1:8000 and NGINX proxy_pass matches.
- CORS errors: set `CORS_ORIGINS` in `.env.production` to your frontend domains.
- DB errors: verify `DATABASE_URL` and that DB user has privileges.

## Notes
- Gunicorn uses the app factory via `app.py` (Procfile `app:app`).
- Render `render.yaml` wires DB/Redis services automatically; for VPS use your own services.

## Rollback

### Render
- Open your Web Service → Deploys/Events in the Render dashboard.
- Select the last successful deploy and click "Rollback" (or redeploy a previous successful image).
- Optionally, disable auto-deploy temporarily while investigating.

### VPS
- Revert code to a known-good version:
  - `cd /home/deploy/routeforce && git fetch --all && git checkout <tag-or-commit>`
  - `source venv/bin/activate && pip install -r requirements.txt`
  - If migrations changed, consider: `flask db stamp head` followed by `flask db upgrade` or restore DB from backup.
  - `sudo systemctl restart routeforce`
- Keep a tarball of the last good release for faster rollback.
