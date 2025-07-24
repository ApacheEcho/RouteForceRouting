#!/bin/bash

# RouteForce DNS Monitor and Fix Guide
# Monitors DNS status and provides guidance for Google Cloud DNS setup

echo "🚀 RouteForce DNS Configuration Monitor"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check DNS resolution
check_dns() {
    local domain=$1
    local expected=$2
    
    echo -e "${BLUE}Checking DNS for $domain...${NC}"
    
    # Try nslookup first
    result=$(nslookup "$domain" 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    
    if [ -z "$result" ]; then
        # Try dig as backup
        result=$(dig +short "$domain" CNAME 2>/dev/null)
    fi
    
    if [ -z "$result" ]; then
        echo -e "${RED}❌ DNS not configured for $domain${NC}"
        return 1
    else
        echo -e "${GREEN}✅ DNS found: $domain → $result${NC}"
        if [[ "$result" == *"$expected"* ]]; then
            return 0
        else
            echo -e "${YELLOW}⚠️  DNS points to unexpected target${NC}"
            return 2
        fi
    fi
}

# Function to check website accessibility
check_website() {
    local url=$1
    
    echo -e "${BLUE}Checking website accessibility: $url${NC}"
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10)
    
    if [ "$status" = "200" ]; then
        echo -e "${GREEN}✅ Website is accessible (HTTP $status)${NC}"
        return 0
    elif [ "$status" = "000" ]; then
        echo -e "${RED}❌ Website not reachable (connection failed)${NC}"
        return 1
    else
        echo -e "${YELLOW}⚠️  Website returned HTTP $status${NC}"
        return 2
    fi
}

# Function to display current DNS nameservers
check_nameservers() {
    echo -e "${BLUE}Checking current DNS nameservers...${NC}"
    
    nameservers=$(dig +short NS routeforcepro.com | sort)
    
    echo "Current nameservers for routeforcepro.com:"
    echo "$nameservers" | while read ns; do
        echo "  - $ns"
    done
    
    if echo "$nameservers" | grep -q "googledomains.com"; then
        echo -e "${GREEN}✅ Confirmed: Using Google Cloud DNS${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Unexpected nameservers detected${NC}"
        return 1
    fi
}

# Function to display next steps
show_next_steps() {
    echo ""
    echo "🎯 NEXT STEPS TO FIX DNS:"
    echo "========================"
    echo ""
    echo -e "${YELLOW}Since your domain uses Google Cloud DNS:${NC}"
    echo ""
    echo "1. 🌐 Go to Google Cloud Console:"
    echo "   https://console.cloud.google.com/"
    echo ""
    echo "2. 📋 Navigate to: Network Services → Cloud DNS"
    echo ""
    echo "3. 🔍 Find the zone for: routeforcepro.com"
    echo ""
    echo "4. ➕ Add CNAME Record:"
    echo "   Name: app"
    echo "   Type: CNAME"
    echo "   TTL: 3600"
    echo "   Data: routeforcepro.netlify.app"
    echo ""
    echo -e "${BLUE}Alternative: Contact Squarespace Support${NC}"
    echo "Ask them to add the CNAME record via Google Cloud DNS"
    echo ""
    echo -e "${GREEN}After adding the record, run this script again to monitor propagation.${NC}"
    echo ""
}

# Main monitoring loop
main() {
    echo "Starting DNS configuration check..."
    echo ""
    
    # Check nameservers first
    check_nameservers
    echo ""
    
    # Check if custom domain DNS is configured
    if check_dns "app.routeforcepro.com" "routeforcepro.netlify.app"; then
        echo ""
        echo -e "${GREEN}🎉 DNS is configured correctly!${NC}"
        echo ""
        
        # Check if website is accessible
        if check_website "https://app.routeforcepro.com"; then
            echo ""
            echo -e "${GREEN}🚀 SUCCESS! Your RouteForce app is live at:${NC}"
            echo -e "${GREEN}   https://app.routeforcepro.com${NC}"
            echo ""
            echo "✅ DNS configuration complete"
            echo "✅ SSL certificate active"
            echo "✅ Website accessible"
            echo ""
            echo "🎯 Your RouteForce application is now fully deployed!"
            return 0
        else
            echo ""
            echo -e "${YELLOW}DNS is configured but website not yet accessible.${NC}"
            echo "This is normal - SSL certificate provisioning can take a few minutes."
            echo ""
            echo "Try again in 5-10 minutes, or check Netlify dashboard for SSL status."
        fi
    else
        echo ""
        show_next_steps
    fi
    
    # Check if Netlify site is working
    echo ""
    echo "Verifying Netlify deployment..."
    if check_website "https://routeforcepro.netlify.app"; then
        echo -e "${GREEN}✅ Netlify deployment is working correctly${NC}"
    else
        echo -e "${RED}❌ Issue with Netlify deployment${NC}"
    fi
    
    echo ""
    echo "🔄 Run this script again after adding the DNS record to monitor propagation."
    echo ""
}

# Run main function
main "$@"
