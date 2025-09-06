# 🚀 Render Setup Guide - RouteForce Routing

## ✅ Current Status
- **API Key**: Configure `RENDER_API_KEY` in your environment or GitHub Secrets (do not commit real keys)
- **GitHub Secret**: Set (`RENDER_API_KEY`)
- **Existing Services**: 1 service detected in your account

## 🏗️ Next Steps: Create Render Services

### 1. Access Render Dashboard
Go to: **https://dashboard.render.com/**

### 2. Create Web Service (Main Application)
1. Click **"New +"** → **"Web Service"**
2. **Repository**: Connect your GitHub repository `ApacheEcho/RouteForceRouting`
3. **Configuration**:
   - **Name**: `routeforce-app` (or `routeforce-staging` for staging)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.production`
   - **Plan**: `Starter` (or higher for production)
   - **Region**: `Oregon` (or your preferred region)

4. **Environment Variables** (in Render dashboard):
   ```
   FLASK_ENV=production
   PORT=5000
   PYTHONPATH=/app
   SECRET_KEY=your-super-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```
   Note: The application defaults to port 8000 in production if `PORT` is not set.
   Render explicitly sets `PORT=5000`, so keep this value in Render environments.

5. **Auto-Deploy**: Enable auto-deploy from `main` branch for staging, `production` branch for production

### 3. Create PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. **Configuration**:
   - **Name**: `routeforce-postgres`
   - **Plan**: `Starter` (free tier available)
   - **Region**: Same as web service
   - **Database Name**: `routeforce`
   - **User**: `routeforce`

3. **Copy Connection String**: After creation, copy the `External Database URL`

### 4. Create Redis Cache
1. Click **"New +"** → **"Redis"**
2. **Configuration**:
   - **Name**: `routeforce-redis`
   - **Plan**: `Starter` (free tier available)
   - **Region**: Same as web service

3. **Copy Connection String**: After creation, copy the `Redis URL`

### 5. Update Web Service Environment Variables
Go back to your web service and add:
```
DATABASE_URL=postgresql://[copied from PostgreSQL service]
REDIS_URL=redis://[copied from Redis service]
```

### 6. Get Service IDs
After creating services, you'll see the Service ID in the URL:
- Format: `https://dashboard.render.com/web/srv-xxxxxxxxx`
- The `srv-xxxxxxxxx` part is your Service ID

### 6.1 Get a Deploy Hook (Recommended for CI)
1. Open your Web Service → Settings → Deploy hooks
2. Click "New Deploy Hook", name it, and copy the generated URL
3. Save it as GitHub Secret `RENDER_DEPLOY_HOOK`

### 7. Set GitHub Secrets
Run these commands with your actual Service IDs:

```bash
# For staging service
gh secret set RENDER_STAGING_SERVICE_ID --body="srv-your-staging-id"

# For production service (if separate)
gh secret set RENDER_PRODUCTION_SERVICE_ID --body="srv-your-production-id"

# Additional secrets for full CI/CD
gh secret set DOCKER_USERNAME --body="your-docker-username"
gh secret set DOCKER_PASSWORD --body="your-docker-token"
gh secret set CODECOV_TOKEN --body="your-codecov-token"
gh secret set SENTRY_DSN --body="https://your-sentry-dsn@sentry.io/project-id"
gh secret set SLACK_WEBHOOK_URL --body="https://hooks.slack.com/services/your/webhook"

# Recommended simple path (Deploy Hook)
gh secret set RENDER_DEPLOY_HOOK --body="https://api.render.com/deploy/srv-xxxxxxxx?key=..."

# Optional: protect /metrics with a token and set allowed CORS origins
gh secret set METRICS_TOKEN --body="<random-token>"
gh secret set CORS_ORIGINS --body="https://app.routeforcepro.com"
gh secret set HEALTHCHECK_URL --body="https://<your-domain>/health"  # used by CI to poll service readiness
gh secret set METRICS_URL --body="https://<your-domain>/metrics"   # used by CI to validate metrics
```

## 🧪 Testing Your Setup

### Test 1: Validate Configuration
```bash
./scripts/deploy-render.sh validate
```

### Test 2: Dry Run Deployment
```bash
./scripts/deploy-render.sh deploy --environment staging --dry-run
```

### Test 3: Actual Staging Deployment
```bash
./scripts/deploy-render.sh deploy --environment staging
```

## 📋 Environment URLs (After Setup)
- **Staging**: `https://your-app-name.onrender.com`
- **Production**: `https://your-production-app.onrender.com`

## 🔍 Monitoring Your Services

### Check Service Status
```bash
./scripts/deploy-render.sh status --environment staging
```

### View Logs
```bash
./scripts/deploy-render.sh logs --environment staging
```

### Health Check
```bash
./scripts/deploy-render.sh health --environment staging
```

## ⚠️ Common Issues

1. **Build Failures**: Check Dockerfile.production builds locally first
2. **Database Connection**: Ensure DATABASE_URL is correctly set
3. **Port Issues**: Render requires your app to bind to `0.0.0.0:5000`
4. **Health Checks**: Your app must respond to `/health` endpoint

## 📞 Support
- **Render Docs**: https://render.com/docs
- **GitHub Actions**: Already configured in `.github/workflows/render-deploy.yml`
- **Deployment Scripts**: Available in `scripts/` directory

---
**Next Action**: Create the services in Render dashboard, then run the test commands above! 🚀
