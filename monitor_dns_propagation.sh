#!/bin/bash
# DNS Propagation Monitoring for app.routeforcepro.com

echo "🔍 DNS Propagation Monitor for app.routeforcepro.com"
echo "=================================================="

check_dns() {
    local server=$1
    local name=$2
    echo -n "Testing $name ($server): "
    
    if timeout 5 nslookup app.routeforcepro.com "$server" > /dev/null 2>&1; then
        result=$(nslookup app.routeforcepro.com "$server" 2>/dev/null | grep -A1 "canonical name" | tail -1 | awk '{print $NF}' | sed 's/\.$//')
        if [ "$result" = "routeforcepro.netlify.app" ]; then
            echo "✅ RESOLVED"
            return 0
        else
            echo "⚠️  PARTIAL ($result)"
            return 1
        fi
    else
        echo "❌ NO RESOLUTION"
        return 1
    fi
}

echo "Testing major DNS servers:"
check_dns "8.8.8.8" "Google DNS"
check_dns "1.1.1.1" "Cloudflare DNS"
check_dns "208.67.222.222" "OpenDNS"
check_dns "9.9.9.9" "Quad9 DNS"

echo
echo "Direct test:"
if curl -I https://app.routeforcepro.com 2>/dev/null | head -1 | grep -q "200"; then
    echo "✅ https://app.routeforcepro.com is LIVE!"
else
    echo "⏳ https://app.routeforcepro.com not yet accessible"
fi

echo
echo "Next steps:"
echo "- If no resolution: Add DNS record in Google Domains"
echo "- If partial: Wait for propagation (15min-24hrs)"
echo "- If live: Configure Netlify domain settings"
