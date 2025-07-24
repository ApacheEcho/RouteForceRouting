#!/bin/bash

# Enhanced RouteForce DNS Configuration Monitor
# Provides step-by-step guidance and real-time monitoring

echo "🚀 RouteForce Enhanced DNS Monitor & Guide"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Function to show progress bar
show_progress() {
    local duration=$1
    local message=$2
    echo -e "${BLUE}$message${NC}"
    for ((i=1; i<=duration; i++)); do
        printf "█"
        sleep 1
    done
    echo ""
}

# Function to check DNS with multiple methods
comprehensive_dns_check() {
    local domain=$1
    local target=$2
    
    echo -e "${PURPLE}🔍 Comprehensive DNS Analysis for $domain${NC}"
    echo "================================================"
    
    # Method 1: nslookup
    echo -e "${BLUE}Method 1: nslookup${NC}"
    nslookup_result=$(nslookup "$domain" 8.8.8.8 2>/dev/null)
    if echo "$nslookup_result" | grep -q "NXDOMAIN\|can't find"; then
        echo -e "${RED}❌ nslookup: Domain not found${NC}"
    elif echo "$nslookup_result" | grep -q "$target"; then
        echo -e "${GREEN}✅ nslookup: Correctly points to $target${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  nslookup: Points to different target${NC}"
        echo "$nslookup_result" | grep -A1 "Name:"
    fi
    
    # Method 2: dig
    echo -e "${BLUE}Method 2: dig${NC}"
    dig_result=$(dig +short "$domain" CNAME @8.8.8.8 2>/dev/null)
    if [ -z "$dig_result" ]; then
        echo -e "${RED}❌ dig: No CNAME record found${NC}"
    elif echo "$dig_result" | grep -q "$target"; then
        echo -e "${GREEN}✅ dig: Correctly points to $target${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  dig: Points to $dig_result${NC}"
    fi
    
    # Method 3: Alternative DNS servers
    echo -e "${BLUE}Method 3: Multiple DNS servers${NC}"
    for dns_server in "1.1.1.1" "8.8.4.4" "208.67.222.222"; do
        result=$(dig +short "$domain" CNAME @"$dns_server" 2>/dev/null)
        if [ -n "$result" ]; then
            echo -e "${GREEN}✅ $dns_server: $result${NC}"
            if echo "$result" | grep -q "$target"; then
                return 0
            fi
        else
            echo -e "${RED}❌ $dns_server: No record${NC}"
        fi
    done
    
    return 1
}

# Function to check website with detailed analysis
comprehensive_site_check() {
    local url=$1
    
    echo -e "${PURPLE}🌐 Website Accessibility Analysis: $url${NC}"
    echo "================================================"
    
    # HTTP status check
    echo -e "${BLUE}Checking HTTP status...${NC}"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 15)
    
    case $status in
        200)
            echo -e "${GREEN}✅ HTTP 200: Website is accessible${NC}"
            ;;
        301|302)
            echo -e "${YELLOW}↩️  HTTP $status: Redirect detected${NC}"
            redirect_location=$(curl -s -I "$url" --max-time 10 | grep -i location | cut -d' ' -f2 | tr -d '\r')
            echo -e "${BLUE}   Redirects to: $redirect_location${NC}"
            ;;
        404)
            echo -e "${RED}❌ HTTP 404: Page not found${NC}"
            ;;
        000)
            echo -e "${RED}❌ Connection failed: DNS or network issue${NC}"
            ;;
        *)
            echo -e "${YELLOW}⚠️  HTTP $status: Unexpected response${NC}"
            ;;
    esac
    
    # SSL certificate check
    if [[ "$url" == https* ]]; then
        echo -e "${BLUE}Checking SSL certificate...${NC}"
        ssl_info=$(echo | openssl s_client -servername "$(echo "$url" | sed 's|https://||' | cut -d'/' -f1)" -connect "$(echo "$url" | sed 's|https://||' | cut -d'/' -f1):443" 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null)
        
        if [ $? -eq 0 ] && [ -n "$ssl_info" ]; then
            echo -e "${GREEN}✅ SSL certificate is valid${NC}"
            echo "$ssl_info" | grep "notAfter" | sed 's/notAfter=/   Expires: /'
        else
            echo -e "${RED}❌ SSL certificate issue${NC}"
        fi
    fi
    
    # Response headers check
    echo -e "${BLUE}Checking response headers...${NC}"
    headers=$(curl -s -I "$url" --max-time 10)
    if echo "$headers" | grep -qi "netlify"; then
        echo -e "${GREEN}✅ Served by Netlify${NC}"
    fi
    if echo "$headers" | grep -qi "content-security-policy"; then
        echo -e "${GREEN}✅ Security headers present${NC}"
    fi
    
    return $([ "$status" = "200" ] && echo 0 || echo 1)
}

# Function to provide step-by-step Google Cloud DNS guidance
show_google_cloud_guidance() {
    echo -e "${CYAN}📋 STEP-BY-STEP GOOGLE CLOUD DNS SETUP${NC}"
    echo "======================================"
    echo ""
    echo -e "${YELLOW}🎯 Your domain uses Google Cloud DNS. Follow these exact steps:${NC}"
    echo ""
    
    echo -e "${BLUE}Step 1: Access Google Cloud Console${NC}"
    echo "   🌐 Go to: https://console.cloud.google.com/"
    echo "   🔑 Sign in with your Google account"
    echo ""
    
    echo -e "${BLUE}Step 2: Navigate to Cloud DNS${NC}"
    echo "   📋 Click: ☰ Menu → Network Services → Cloud DNS"
    echo "   🔍 Look for: Zone named 'routeforcepro.com' or similar"
    echo ""
    
    echo -e "${BLUE}Step 3: Add DNS Record${NC}"
    echo "   ➕ Click: 'Add Record Set' button"
    echo "   📝 Fill in the form:"
    echo "      DNS Name: app"
    echo "      Resource Record Type: CNAME"
    echo "      TTL: 3600"
    echo "      Canonical name: routeforcepro.netlify.app"
    echo ""
    
    echo -e "${BLUE}Step 4: Save and Wait${NC}"
    echo "   💾 Click: 'Create' button"
    echo "   ⏱️  Wait: 5-30 minutes for DNS propagation"
    echo ""
    
    echo -e "${YELLOW}🆘 Can't access Google Cloud Console?${NC}"
    echo "   📞 Contact Squarespace Support"
    echo "   💬 Say: 'Need CNAME record added via Google Cloud DNS'"
    echo "   📋 Provide: Domain=routeforcepro.com, Subdomain=app, Target=routeforcepro.netlify.app"
    echo ""
}

# Function to monitor DNS propagation in real-time
monitor_dns_propagation() {
    local domain="app.routeforcepro.com"
    local target="routeforcepro.netlify.app"
    local max_attempts=20
    local attempt=1
    
    echo -e "${PURPLE}🔄 Real-time DNS Propagation Monitor${NC}"
    echo "===================================="
    echo ""
    echo -e "${BLUE}Monitoring DNS propagation for $domain...${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop monitoring${NC}"
    echo ""
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}Attempt $attempt/$max_attempts - $(date)${NC}"
        
        if comprehensive_dns_check "$domain" "$target"; then
            echo ""
            echo -e "${GREEN}🎉 DNS PROPAGATION SUCCESSFUL!${NC}"
            echo ""
            
            # Test the actual website
            echo -e "${BLUE}Testing website accessibility...${NC}"
            if comprehensive_site_check "https://$domain"; then
                echo ""
                echo -e "${GREEN}🚀 SUCCESS! Your RouteForce app is live at:${NC}"
                echo -e "${GREEN}   https://$domain${NC}"
                echo ""
                echo -e "${GREEN}✅ Deployment Complete!${NC}"
                echo "✅ DNS configured correctly"
                echo "✅ SSL certificate active"
                echo "✅ Website accessible"
                echo "✅ Netlify serving content"
                return 0
            else
                echo -e "${YELLOW}⚠️  DNS works but website not yet accessible${NC}"
                echo -e "${BLUE}This is normal - SSL provisioning can take a few more minutes${NC}"
            fi
            return 0
        fi
        
        echo -e "${RED}❌ DNS not yet propagated${NC}"
        echo ""
        
        if [ $attempt -lt $max_attempts ]; then
            echo -e "${BLUE}Waiting 30 seconds before next check...${NC}"
            sleep 30
        fi
        
        attempt=$((attempt + 1))
    done
    
    echo -e "${YELLOW}⏰ DNS propagation taking longer than expected${NC}"
    echo -e "${BLUE}This is normal and can take up to 24 hours${NC}"
    echo -e "${BLUE}Continue monitoring by running this script again later${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting comprehensive DNS analysis...${NC}"
    echo ""
    
    # Check current nameservers
    echo -e "${PURPLE}🌐 DNS Infrastructure Analysis${NC}"
    echo "=============================="
    nameservers=$(dig +short NS routeforcepro.com | sort)
    echo "Current nameservers for routeforcepro.com:"
    echo "$nameservers" | while read ns; do
        echo "  🌐 $ns"
    done
    
    if echo "$nameservers" | grep -q "googledomains.com"; then
        echo -e "${GREEN}✅ Confirmed: Using Google Cloud DNS${NC}"
    else
        echo -e "${YELLOW}⚠️  Unexpected nameservers detected${NC}"
    fi
    echo ""
    
    # Check if DNS is already configured
    if comprehensive_dns_check "app.routeforcepro.com" "routeforcepro.netlify.app"; then
        echo ""
        echo -e "${GREEN}🎉 DNS is already configured correctly!${NC}"
        
        # Check website accessibility
        if comprehensive_site_check "https://app.routeforcepro.com"; then
            echo ""
            echo -e "${GREEN}🚀 DEPLOYMENT COMPLETE!${NC}"
            echo -e "${GREEN}Your RouteForce app is live at: https://app.routeforcepro.com${NC}"
            return 0
        else
            echo ""
            echo -e "${YELLOW}DNS configured but website not yet accessible${NC}"
            echo -e "${BLUE}SSL certificate may still be provisioning...${NC}"
        fi
    else
        echo ""
        echo -e "${RED}❌ DNS not yet configured${NC}"
        echo ""
        show_google_cloud_guidance
        
        # Ask if user wants to monitor
        echo -e "${YELLOW}Would you like to start real-time DNS monitoring? (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy] ]]; then
            monitor_dns_propagation
        fi
    fi
    
    # Always check Netlify deployment
    echo ""
    echo -e "${PURPLE}🚀 Netlify Deployment Status${NC}"
    echo "=========================="
    if comprehensive_site_check "https://routeforcepro.netlify.app"; then
        echo -e "${GREEN}✅ Netlify deployment is working perfectly${NC}"
    else
        echo -e "${RED}❌ Issue with Netlify deployment${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}📋 Next Steps:${NC}"
    echo "1. Add the CNAME record in Google Cloud Console"
    echo "2. Run this script again to monitor propagation"
    echo "3. Once DNS propagates, https://app.routeforcepro.com will be live!"
    echo ""
}

# Execute main function
main "$@"
