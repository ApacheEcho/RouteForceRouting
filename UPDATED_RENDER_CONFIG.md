# 🚀 Updated Render Deployment Configuration

## ✅ Corrected Service Information
- **Service ID**: `srv-d21l9rngi27c73e2js7g`
- **Deploy Hook**: `https://api.render.com/deploy/srv-d21l9rngi27c73e2js7g`

## 🔐 Recommended Setup (Deploy Hook - Simpler)

### Step 1: Add GitHub Secret
1. Go to: https://github.com/ApacheEcho/RouteForceRouting/settings/secrets/actions
2. Click "New repository secret"
3. Add:
   - **Name**: `RENDER_DEPLOY_HOOK`
   - **Value**: `https://api.render.com/deploy/srv-d21l9rngi27c73e2js7g`

### Step 2: Test Deployment
After setting the secret, test by:
- Pushing to main branch, OR
- Manual workflow dispatch in GitHub Actions

## 🔧 Alternative Setup (API Method - More Control)

If you prefer API-based deployment (allows cache clearing, more options):

1. **Name**: `RENDER_SERVICE_ID`
   **Value**: `srv-d21l9rngi27c73e2js7g`

2. **Name**: `RENDER_API_KEY`
   **Value**: `rnd_KYXIprehTG8MKVcR0fi99TRQdEiK`

## ⚠️ Important Notes

1. **Service ID Changed**: The correct service ID is `srv-d21l9rngi27c73e2js7g`, not the previous `tea-d1n35jeuk2gs739fsvq0`
2. **Deploy Hook Preferred**: For most use cases, the deploy hook method is simpler and more reliable
3. **Unauthorized Response**: The "Unauthorized" response suggests the deploy hook needs to be properly configured in Render dashboard first

## 🧪 Test Commands

```bash
# Test deploy hook (after GitHub secret is set)
curl -X POST https://api.render.com/deploy/srv-d21l9rngi27c73e2js7g

# Test API method (if using API secrets)
curl -X POST \
  -H "Authorization: Bearer rnd_KYXIprehTG8MKVcR0fi99TRQdEiK" \
  -H "Content-Type: application/json" \
  -d '{"serviceId":"srv-d21l9rngi27c73e2js7g","clearCache":true}' \
  "https://api.render.com/v1/services/srv-d21l9rngi27c73e2js7g/deploys"
```

## 🎯 Next Steps

1. **Check Render Dashboard**: Ensure deploy hooks are enabled for your service
2. **Set GitHub Secret**: Use the deploy hook method (recommended)
3. **Test Deployment**: Push to main or trigger manually
4. **Monitor**: Check both GitHub Actions and Render dashboard

The GitHub Actions workflow is already configured to handle both methods automatically!
