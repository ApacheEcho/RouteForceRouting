# Production Deployment Guide

## 1. Build Frontend
```
cd frontend && npm run build
```

## 2. Start Flask with Gunicorn
```
# Bind to the port your runtime expects.
# The app defaults to 8000 in production if PORT is not set.
# Many platforms (e.g., Render) require 5000.
gunicorn -w 4 -b 0.0.0.0:${PORT:-8000} gunicorn_entry:app
```

## 3. Configure Nginx
See `nginx.sample.conf` for a sample config. Place it in your Nginx sites-available and enable it.
Adjust the upstream port to match your app's PORT (5000 or 8000) or set `PORT` explicitly to avoid drift.

## 4. Enable HTTPS
Use Certbot or another tool to obtain SSL certificates and enable HTTPS in your Nginx config.

## 5. Environment Variables
Set secrets and config in `.env` files. Do not hardcode sensitive values.

## 6. Monitoring & Logging
Integrate Sentry, logging, and monitoring as needed for production.

## 7. Automated Deployment
Consider Docker or CI/CD for automated builds and deployments.
