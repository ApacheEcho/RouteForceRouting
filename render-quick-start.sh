#!/bin/bash

# Quick Render Setup Assistant for RouteForce
# Helps you get started with Render deployment

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
action() { echo -e "${PURPLE}🚀 $1${NC}"; }

echo "🎯 RouteForce Render Setup Assistant"
echo "======================================"

# Check current status
log "Current Status Check:"

# API Key
if [[ -n "${RENDER_API_KEY:-}" ]]; then
    log "RENDER_API_KEY is set"
else
    warn "RENDER_API_KEY not set in environment"
    info "Your API key: rnd_B8CME7w4qoHjZJwDctoxNqMZzNHd"
    export RENDER_API_KEY=rnd_B8CME7w4qoHjZJwDctoxNqMZzNHd
fi

# Check GitHub secrets
echo ""
info "GitHub Repository Secrets Status:"
gh secret list | grep RENDER || echo "No RENDER secrets found"

echo ""
action "Next Steps for Complete Setup:"
echo ""
echo "1. 🌐 Open Render Dashboard:"
echo "   https://dashboard.render.com/"
echo ""
echo "2. 🏗️ Create Services (follow RENDER_SETUP_GUIDE.md):"
echo "   • Web Service (RouteForce App)"
echo "   • PostgreSQL Database" 
echo "   • Redis Cache"
echo ""
echo "3. 🔑 Get Service IDs from URLs:"
echo "   • Look for 'srv-xxxxxxxxx' in service URLs"
echo "   • Set as GitHub secrets"
echo ""
echo "4. 🧪 Test Deployment:"
echo "   ./scripts/deploy-render.sh deploy --environment staging --dry-run"
echo ""

# Check if services exist
python3 get-render-services.py

echo ""
echo "📚 Available Resources:"
echo "   • Complete Guide: RENDER_SETUP_GUIDE.md"
echo "   • Deployment Checklist: RENDER_DEPLOYMENT_CHECKLIST.md"
echo "   • Environment Config: .env.render"
echo ""
echo "🎉 Your API key is configured and ready!"
echo "   Follow the guide above to complete your Render setup."
