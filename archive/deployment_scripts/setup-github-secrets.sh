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
