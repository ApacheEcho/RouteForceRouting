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
