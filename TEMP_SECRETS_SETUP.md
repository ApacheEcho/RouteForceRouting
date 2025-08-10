# 🛡️ GitHub Secrets Setup - IMMEDIATE ACTION REQUIRED

## Critical Security Notice
The following sensitive information should be added to GitHub Secrets IMMEDIATELY and then deleted from any local files.

## Required GitHub Repository Secrets

### Step 1: Navigate to GitHub Secrets
1. Go to: https://github.com/ApacheEcho/RouteForceRouting
2. Click: Settings → Secrets and variables → Actions
3. Click: "New repository secret"

### Step 2: Add Required Secrets

**Secret 1:**
- Name: `RENDER_API_KEY`
- Value: `rnd_KYXIprehTG8MKVcR0fi99TRQdEiK`

**Secret 2:**
- Name: `RENDER_SERVICE_ID`
- Value: `srv-d21l9rngi27c73e2js7g`

### Step 3: Verify Configuration
After adding secrets, the GitHub Actions workflow will:
- ✅ Use API-based deployment (more reliable than deploy hooks)
- ✅ Support cache clearing and advanced deployment options
- ✅ Provide detailed success/failure feedback

### Step 4: Test Deployment
Once configured, test by:
1. Pushing to main branch, OR
2. Manual workflow dispatch in GitHub Actions

## Security Reminder
🚨 DELETE this file after setting up secrets - it contains sensitive information!

## Alternative: Deploy Hook (Simpler but less control) - RECOMMENDED
If you prefer a simpler setup, you can use a deploy hook instead:
- Name: `RENDER_DEPLOY_HOOK`
- Value: `https://api.render.com/deploy/srv-d21l9rngi27c73e2js7g`

This would replace both API_KEY and SERVICE_ID secrets.
