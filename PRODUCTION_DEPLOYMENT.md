# Production Deployment Guide

## 1. Build Frontend
```
cd frontend && npm run build
```

## 2. Start Flask with Gunicorn
```
gunicorn -w 4 -b 0.0.0.0:5000 gunicorn_entry:app
```

## 3. Configure Nginx
See `nginx.sample.conf` for a sample config. Place it in your Nginx sites-available and enable it.

## 4. Enable HTTPS
Use Certbot or another tool to obtain SSL certificates and enable HTTPS in your Nginx config.

## 5. Environment Variables
Set secrets and config in `.env` files. Do not hardcode sensitive values.

## 6. Monitoring & Logging
Integrate Sentry, logging, and monitoring as needed for production.

## 7. Automated Deployment
Consider Docker or CI/CD for automated builds and deployments.
