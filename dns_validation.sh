#!/bin/bash
# DNS Configuration Validation Script for app.routeforcepro.com

echo "🔍 DNS Configuration Validation for app.routeforcepro.com"
echo "=================================================="
echo

# Check if main domain exists
echo "1. Checking main domain (routeforcepro.com)..."
if nslookup routeforcepro.com > /dev/null 2>&1; then
    echo "   ✅ routeforcepro.com resolves correctly"
else
    echo "   ❌ routeforcepro.com does not resolve"
fi
echo

# Check subdomain
echo "2. Checking subdomain (app.routeforcepro.com)..."
if nslookup app.routeforcepro.com > /dev/null 2>&1; then
    echo "   ✅ app.routeforcepro.com resolves"
    echo "   📋 DNS Record:"
    nslookup app.routeforcepro.com | grep -E "(Name|CNAME|Address)"
else
    echo "   ❌ app.routeforcepro.com does not resolve (NXDOMAIN)"
    echo "   🔧 DNS record needs to be added"
fi
echo

# Check Netlify direct URL
echo "3. Checking Netlify direct URL..."
if curl -I https://routeforcepro.netlify.app 2>/dev/null | head -1 | grep -q "200"; then
    echo "   ✅ routeforcepro.netlify.app is working"
else
    echo "   ❌ routeforcepro.netlify.app is not responding"
fi
echo

# Check if custom domain works
echo "4. Testing custom domain access..."
if curl -I https://app.routeforcepro.com 2>/dev/null | head -1 | grep -q "200"; then
    echo "   ✅ app.routeforcepro.com is working!"
    echo "   🎉 DNS configuration is complete"
elif curl -s https://app.routeforcepro.com 2>&1 | grep -q "Could not resolve host"; then
    echo "   ❌ app.routeforcepro.com - DNS resolution failed"
    echo "   📝 Action needed: Add CNAME record"
else
    echo "   ⚠️  app.routeforcepro.com - DNS works but site not responding"
    echo "   📝 Action needed: Check Netlify domain configuration"
fi
echo

# DNS Servers check
echo "5. Checking DNS servers for routeforcepro.com..."
echo "   📋 Name servers:"
dig routeforcepro.com NS +short | sed 's/^/      /'
echo

# Provide next steps
echo "🎯 NEXT STEPS:"
echo "==============="

if ! nslookup app.routeforcepro.com > /dev/null 2>&1; then
    echo "1. 🌐 Add DNS Record in Google Domains:"
    echo "   - Go to: https://domains.google.com"
    echo "   - Domain: routeforcepro.com → DNS"
    echo "   - Add: CNAME | app | routeforcepro.netlify.app"
    echo
    echo "2. ⏰ Wait for propagation (15 min - 24 hours)"
    echo
    echo "3. 🔄 Run this script again to verify"
else
    echo "1. ✅ DNS is configured correctly"
    echo "2. 🔧 Check Netlify dashboard for domain configuration"
    echo "3. 🕐 If recently added, wait for SSL certificate"
fi
echo

echo "📞 Support Resources:"
echo "- DNS Checker: https://dnschecker.org"
echo "- Netlify Dashboard: https://app.netlify.com"
echo "- Google Domains: https://domains.google.com"
echo

echo "🔍 To check propagation progress:"
echo "   nslookup app.routeforcepro.com 8.8.8.8"
echo "   nslookup app.routeforcepro.com 1.1.1.1"
