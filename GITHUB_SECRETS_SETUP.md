# 🔐 GitHub Repository Secrets Setup Guide

After fixing the GitHub Actions workflow errors, many features are disabled with `if: false` conditions until proper secrets are configured. This guide explains how to set up the missing secrets to enable all features.

## 🎯 Quick Setup Priority

### **Essential (Recommended First)**
1. `CODECOV_TOKEN` - Code coverage reporting ✅ Already configured in CI/CD
2. `RENDER_API_KEY` - Deployment to Render.com

### **Optional (Advanced Features)**  
3. `SENTRY_AUTH_TOKEN` - Error monitoring integration
4. `SENTRY_DSN` - Application error tracking

---

## 🛠️ Setting Up GitHub Repository Secrets

### 1. Navigate to Repository Settings
- Go to your GitHub repository: `https://github.com/ApacheEcho/RouteForceRouting`
- Click **Settings** tab
- Click **Secrets and variables** → **Actions**
- Click **New repository secret**

### 2. Add Required Secrets

#### 📊 **CODECOV_TOKEN** (Code Coverage)
```
Name: CODECOV_TOKEN
Value: [Get from codecov.io after connecting your repo]
```
**How to get:**
1. Visit [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Add your repository
4. Copy the token from repository settings

#### 🚀 **RENDER_API_KEY** (Deployment)
```
Name: RENDER_API_KEY  
Value: [Your Render.com API key]
```
**How to get:**
1. Log into [render.com](https://render.com)
2. Go to Account Settings → API Keys
3. Create new API key
4. Copy the key

#### 🐛 **SENTRY_AUTH_TOKEN** (Error Monitoring)
```
Name: SENTRY_AUTH_TOKEN
Value: [Your Sentry auth token]
```
**How to get:**
1. Log into [sentry.io](https://sentry.io)
2. Go to Settings → Auth Tokens
3. Create token with `project:releases` scope
4. Copy the token

---

## 🔄 Enabling Disabled Features

After adding secrets, remove the `if: false` conditions from these workflow files:

### **render-deploy.yml**
```yaml
# BEFORE (disabled):
- name: Deploy to Render
  if: false # Disabled - configure RENDER_API_KEY to enable

# AFTER (enabled):  
- name: Deploy to Render
  # if: false # Disabled - configure RENDER_API_KEY to enable
```

### **sentry-integration.yml**
```yaml
# Enable these steps:
- name: 🚀 Create Sentry release
  # if: false # Disabled - configure SENTRY_AUTH_TOKEN to enable
```

### **monitoring-health-checks.yml**  
```yaml
# Add your external notifications if desired (email, etc.)
```

---

## ✅ Testing Your Setup

### 1. **Test CI/CD Pipeline**
```bash
git push origin main
```
- Check Actions tab for green builds
- Verify Codecov reports appear

### 2. **Test Deployment**  
```bash
git push origin main
```
- Check Render dashboard for new deployment
- Verify application is accessible

### 3. **Test Error Monitoring**
```bash
# Trigger test error in your app
curl https://your-app.onrender.com/test-error
```
- Check Sentry dashboard for error

---

## 🔧 Current Workflow Status

| Workflow | Status | Required Secrets | Action Needed |
|----------|--------|------------------|---------------|
| CI/CD Pipeline | ✅ Active | CODECOV_TOKEN | Add Codecov token |
| Security Scanning | ✅ Active | None | Ready to use |
| Render Deploy | 🔶 Disabled | RENDER_API_KEY | Add API key + enable |
| Sentry Integration | 🔶 Disabled | SENTRY_AUTH_TOKEN, SENTRY_DSN | Add tokens + enable |

---

## 💡 Pro Tips

### **Environment File Reference**  
Your `.env.render` file contains some credentials that should be added as GitHub secrets:
```bash
# These should become GitHub repository secrets:
DOCKER_USERNAME → Not needed (using GITHUB_TOKEN for GHCR)
DOCKER_PASSWORD → Not needed (using GITHUB_TOKEN for GHCR)  
RENDER_API_KEY → Add as GitHub secret
CODECOV_TOKEN → Add as GitHub secret
```

### **Security Best Practices**
- ✅ Never commit secrets to your repository
- ✅ Use environment-specific secrets for staging/production
- ✅ Regularly rotate API keys and tokens
- ✅ Use least-privilege access for service accounts

### **Gradual Rollout**
1. **Week 1:** Set up essential secrets (Codecov, Render)
2. **Week 2:** Add monitoring (Sentry) 

---

## 🎉 After Setup Complete

Once secrets are configured and workflows enabled, you'll have:

- ✅ **Automated Testing** with coverage reports
- ✅ **Automated Deployment** to Render.com
- ✅ **Security Scanning** with vulnerability reports  
- ✅ **Error Monitoring** with Sentry integration

Your RouteForce application will have enterprise-grade CI/CD! 🚀

---

*Created: $(date)*  
*Last Updated: After workflow error fixes - Batch 1 & 2 complete*
