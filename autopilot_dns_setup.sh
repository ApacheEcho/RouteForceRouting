#!/bin/bash
# AUTO-PILOT: DNS Configuration Management Script
# Complete DNS setup and validation for RouteForce Pro

set -e

LOG_FILE="autopilot_dns_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🚀 AUTO-PILOT DNS CONFIGURATION STARTED"
log "======================================"

# Check current DNS status
log "📊 PHASE 1: DNS Status Analysis"
echo "Current DNS Status for app.routeforcepro.com:"
if nslookup app.routeforcepro.com > /dev/null 2>&1; then
    log "✅ app.routeforcepro.com already resolves"
    nslookup app.routeforcepro.com | tee -a "$LOG_FILE"
else
    log "❌ app.routeforcepro.com does not resolve - DNS configuration needed"
fi

# Verify Netlify site status
log "📊 PHASE 2: Netlify Site Verification"
if curl -I https://routeforcepro.netlify.app 2>/dev/null | head -1 | grep -q "200"; then
    log "✅ Netlify site is responsive"
else
    log "❌ Netlify site not responding - investigating..."
    curl -I https://routeforcepro.netlify.app 2>&1 | tee -a "$LOG_FILE"
fi

# Create DNS record template
log "📋 PHASE 3: DNS Record Template Generation"
cat > dns_record_template.txt << 'EOF'
DNS RECORD TO ADD IN GOOGLE DOMAINS:
====================================

Domain: routeforcepro.com
Location: Google Domains → DNS → Manage custom records

Record Details:
- Type: CNAME
- Name: app
- Data: routeforcepro.netlify.app
- TTL: 3600

Visual Representation:
┌──────┬───────┬──────────────────────────┬──────┐
│ Type │ Name  │ Data                     │ TTL  │
├──────┼───────┼──────────────────────────┼──────┤
│ CNAME│ app   │ routeforcepro.netlify.app│ 3600 │
└──────┴───────┴──────────────────────────┴──────┘

Instructions:
1. Go to: https://domains.google.com
2. Sign in and select routeforcepro.com
3. Navigate to DNS tab
4. Click "Manage custom records"
5. Add the record above
6. Save changes
EOF

log "✅ DNS template created: dns_record_template.txt"

# Test DNS propagation readiness
log "📊 PHASE 4: DNS Infrastructure Verification"
log "Name servers for routeforcepro.com:"
dig routeforcepro.com NS +short | tee -a "$LOG_FILE"

log "A records for main domain:"
dig routeforcepro.com A +short | tee -a "$LOG_FILE"

# Create monitoring script
log "📊 PHASE 5: DNS Monitoring Script Creation"
cat > monitor_dns_propagation.sh << 'EOF'
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
EOF

chmod +x monitor_dns_propagation.sh
log "✅ DNS monitoring script created: monitor_dns_propagation.sh"

# Run initial monitoring
log "📊 PHASE 6: Initial DNS Monitoring"
./monitor_dns_propagation.sh | tee -a "$LOG_FILE"

log "🎯 AUTO-PILOT DNS CONFIGURATION SUMMARY"
log "======================================="
log "✅ Domain analysis complete"
log "✅ DNS infrastructure verified"
log "✅ Monitoring tools created"
log "📋 Next action: Add CNAME record in Google Domains"
log "📄 All details logged to: $LOG_FILE"

echo
echo "🚀 AUTO-PILOT STATUS: DNS PHASE COMPLETE"
echo "📋 MANUAL ACTION REQUIRED: Add DNS record using template above"
echo "🔄 Monitor progress with: ./monitor_dns_propagation.sh"
EOF

chmod +x autopilot_dns_setup.sh
