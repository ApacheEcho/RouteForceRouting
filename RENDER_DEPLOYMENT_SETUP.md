# 🚀 Render Deployment Setup

## Service Configuration
- **Service ID**: `srv-d21l9rngi27c73e2js7g`
- **Platform**: Render.com
- **Deployment Method**: GitHub Actions Workflow

## Quick Setup

### 1. GitHub Secrets (Required)
Set these in your GitHub repository settings:

```bash
# Option A: Deploy Hook (Recommended - Simple)
RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-d21l9rngi27c73e2js7g

# Option B: API Method (More Control)
RENDER_SERVICE_ID=srv-d21l9rngi27c73e2js7g
RENDER_API_KEY=your-render-api-key-here
```

### 2. Deployment Trigger
The workflow automatically deploys when:
- Code is pushed to `main` branch
- Manual trigger via GitHub Actions

### 3. Verify Deployment
After setup, test with:
```bash
# Manual trigger
curl -X POST https://api.render.com/deploy/srv-d21l9rngi27c73e2js7g
```

## Monitoring
- **Render Dashboard**: https://dashboard.render.com/
- **GitHub Actions**: Repository → Actions tab
- **Live App**: Check your Render service URL

## Troubleshooting
1. Verify GitHub secrets are set correctly
2. Check GitHub Actions workflow logs
3. Monitor Render deployment logs
4. Ensure `render.yaml` configuration is correct
