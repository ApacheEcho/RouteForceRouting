#!/bin/bash

# Render Environment Setup Script
# Sets up all required environment variables for Render deployment

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

log "🔧 Setting up Render environment variables..."

# Create .env.render file with required environment variables
cat > .env.render << EOF
# Render Deployment Configuration
# Copy these values to your Render service environment variables

# API Configuration
RENDER_API_KEY=your_render_api_key_here

# Service IDs (Get from Render Dashboard)
RENDER_STAGING_SERVICE_ID=srv-staging-service-id
RENDER_PRODUCTION_SERVICE_ID=srv-production-service-id

# Database Configuration
DATABASE_URL=postgresql://user:password@hostname:port/database
REDIS_URL=redis://hostname:port

# Application Configuration
FLASK_ENV=production
PORT=5000
PYTHONPATH=/app

# Security Configuration
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Third-party Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/slack/webhook

# Feature Flags
DEBUG=false
TESTING=false

# Note: Application defaults to port 8000 in production if PORT is not set.
# Render requires binding to 0.0.0.0:5000; keep PORT=5000 here.

# Performance Configuration
WORKERS=4
TIMEOUT=120
KEEPALIVE=5

# Monitoring
HEALTH_CHECK_ENABLED=true
METRICS_ENABLED=true
EOF

log "✅ Created .env.render with required environment variables"

# Create GitHub Secrets setup script
cat > setup-github-secrets.sh << 'EOF'
#!/bin/bash

# GitHub Secrets Setup for Render CI/CD
echo "Setting up GitHub repository secrets for Render deployment..."

# Required secrets for GitHub Actions
SECRETS=(
    "RENDER_API_KEY:Your Render API key"
    "RENDER_STAGING_SERVICE_ID:Staging service ID from Render"
    "RENDER_PRODUCTION_SERVICE_ID:Production service ID from Render"
    "DOCKER_USERNAME:Docker Hub username"
    "DOCKER_PASSWORD:Docker Hub password or access token"
    "CODECOV_TOKEN:CodeCov API token"
    "SENTRY_DSN:Sentry DSN for error tracking"
    "SLACK_WEBHOOK_URL:Slack webhook for notifications"
)

echo ""
echo "Please set the following secrets in your GitHub repository:"
echo "Go to: Settings > Secrets and variables > Actions"
echo ""

for secret in "${SECRETS[@]}"; do
    IFS=':' read -r name description <<< "$secret"
    echo "• $name - $description"
done

echo ""
echo "Use the GitHub CLI to set secrets:"
echo "gh secret set RENDER_API_KEY --body=\"your_api_key\""
echo "gh secret set RENDER_STAGING_SERVICE_ID --body=\"srv-xxxxxxxxx\""
echo "# ... repeat for all secrets"
EOF

chmod +x setup-github-secrets.sh

log "✅ Created GitHub secrets setup script"

# Create Render service validation script
cat > validate-render-services.py << 'EOF'
#!/usr/bin/env python3

import os
import requests
import sys
from typing import Dict, Any

def validate_render_services():
    """Validate Render services are properly configured."""
    api_key = os.getenv('RENDER_API_KEY')
    if not api_key:
        print("❌ RENDER_API_KEY not set")
        return False
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    try:
        # Get all services
        response = requests.get('https://api.render.com/v1/services', headers=headers)
        response.raise_for_status()
        
        services = response.json()
        print(f"✅ Found {len(services)} Render services")
        
        for service in services:
            name = service.get('name', 'Unknown')
            status = service.get('serviceDetails', {}).get('status', 'unknown')
            service_type = service.get('type', 'unknown')
            print(f"  • {name} ({service_type}) - {status}")
        
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error validating Render services: {e}")
        return False

if __name__ == '__main__':
    if validate_render_services():
        print("✅ Render services validation passed")
        sys.exit(0)
    else:
        print("❌ Render services validation failed")
        sys.exit(1)
EOF

chmod +x validate-render-services.py

log "✅ Created Render services validation script"

# Create deployment checklist
cat > RENDER_DEPLOYMENT_CHECKLIST.md << 'EOF'
# 🚀 Render Deployment Checklist

## Pre-Deployment Setup

### 1. Render Account Setup
- [ ] Create Render account at https://render.com
- [ ] Generate API key from Render Dashboard > Account Settings
- [ ] Note down API key for GitHub Secrets

### 2. Service Configuration
- [ ] Create Web Service for main application
- [ ] Create PostgreSQL database service
- [ ] Create Redis cache service
- [ ] Configure environment variables
- [ ] Set up custom domains (if needed)

### 3. GitHub Configuration
- [ ] Set up GitHub repository secrets (run `./setup-github-secrets.sh`)
- [ ] Verify GitHub Actions workflows are enabled
- [ ] Test deployment pipeline with staging first

### 4. Docker Configuration
- [ ] Verify Dockerfile.production builds successfully
- [ ] Test Docker image locally
- [ ] Configure Docker Hub credentials

## Deployment Steps

### Staging Deployment
1. Push to `main` branch triggers staging deployment
2. Monitor deployment in Render dashboard
3. Run health checks: `./scripts/deploy-render.sh health --environment staging`
4. Validate application functionality

### Production Deployment
1. Create release branch: `git checkout -b production`
2. Push to `production` branch triggers production deployment
3. Monitor deployment carefully
4. Run comprehensive health checks
5. Validate all endpoints and functionality

## Post-Deployment

### Monitoring Setup
- [ ] Configure Sentry error tracking
- [ ] Set up monitoring dashboards
- [ ] Configure alerts for service failures
- [ ] Test backup and recovery procedures

### Performance Optimization
- [ ] Monitor response times
- [ ] Optimize database queries
- [ ] Configure caching strategies
- [ ] Review and adjust resource allocations

## Rollback Procedure
If deployment fails:
1. Run: `./scripts/deploy-render.sh rollback --environment production`
2. Investigate issues in logs
3. Fix problems and redeploy
4. Document lessons learned

## Useful Commands

```bash
# Deploy to staging
./scripts/deploy-render.sh deploy --environment staging

# Deploy to production
./scripts/deploy-render.sh deploy --environment production

# Check deployment status
./scripts/deploy-render.sh status --environment production

# View deployment logs
./scripts/deploy-render.sh logs --environment production

# Run health checks
./scripts/deploy-render.sh health --environment production

# Rollback deployment
./scripts/deploy-render.sh rollback --environment production

# Validate configuration
./scripts/deploy-render.sh validate
```

## Environment URLs
- **Staging**: https://routeforce-staging.onrender.com
- **Production**: https://routeforce-routing.onrender.com

## Support Resources
- [Render Documentation](https://render.com/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
EOF

log "✅ Created comprehensive deployment checklist"

echo ""
log "🎉 Render environment setup completed!"
echo ""
warn "Next steps:"
echo "1. Review .env.render and update with your actual values"
echo "2. Run ./setup-github-secrets.sh to configure GitHub secrets"
echo "3. Follow RENDER_DEPLOYMENT_CHECKLIST.md for complete setup"
echo "4. Test deployment with: ./scripts/deploy-render.sh deploy --environment staging --dry-run"
