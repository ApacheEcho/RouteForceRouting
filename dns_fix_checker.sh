#!/bin/bash
# Quick DNS Fix Checker for app.routeforcepro.com

echo "🔍 Checking DNS Status for app.routeforcepro.com"
echo "=============================================="

# Test DNS resolution
echo "1. Testing DNS resolution..."
if nslookup app.routeforcepro.com > /dev/null 2>&1; then
    echo "   ✅ DNS record exists"
    nslookup app.routeforcepro.com | grep -E "(canonical name|CNAME)"
else
    echo "   ❌ DNS record missing - needs to be added"
fi

# Test if site is accessible
echo "2. Testing site accessibility..."
if curl -I https://app.routeforcepro.com 2>/dev/null | head -1 | grep -q "200"; then
    echo "   ✅ Site is fully working!"
elif curl -s https://app.routeforcepro.com 2>&1 | grep -q "Could not resolve host"; then
    echo "   ❌ DNS not resolving - add CNAME record"
else
    echo "   ⚠️  DNS works but site not ready - check Netlify"
fi

# Show what to do next
echo "3. Next steps:"
if ! nslookup app.routeforcepro.com > /dev/null 2>&1; then
    echo "   📝 Add CNAME: app → routeforcepro.netlify.app"
    echo "   🌐 In Google Domains DNS settings"
else
    echo "   ⏳ Wait for propagation or check Netlify domain config"
fi

echo
echo "🌐 Working URL right now: https://routeforcepro.netlify.app"
