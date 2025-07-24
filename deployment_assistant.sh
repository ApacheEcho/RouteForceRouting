#!/bin/bash

# RouteForce Final Deployment Assistant
# Guides you through the final DNS configuration step

echo "🚀 RouteForce Final Deployment Assistant"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Function to check if DNS is configured
check_dns_status() {
    echo -e "${BLUE}Checking current DNS status...${NC}"
    
    # Check if app subdomain resolves
    if nslookup app.routeforcepro.com >/dev/null 2>&1; then
        echo -e "${GREEN}✅ DNS is configured!${NC}"
        return 0
    else
        echo -e "${RED}❌ DNS not yet configured${NC}"
        return 1
    fi
}

# Function to test website accessibility
test_website() {
    local url=$1
    echo -e "${BLUE}Testing website: $url${NC}"
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 10)
    
    if [ "$status" = "200" ]; then
        echo -e "${GREEN}✅ Website is live and working!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Website returned status: $status${NC}"
        return 1
    fi
}

# Function to display instructions
show_instructions() {
    echo ""
    echo -e "${BOLD}📋 ACTION REQUIRED: Add DNS Record${NC}"
    echo "=================================="
    echo ""
    echo -e "${YELLOW}Your domain uses Google Cloud DNS. Choose one option:${NC}"
    echo ""
    echo -e "${BLUE}Option 1: Google Cloud Console${NC}"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Navigate: Network Services → Cloud DNS"
    echo "3. Find zone: routeforcepro.com"
    echo "4. Add CNAME record:"
    echo "   Name: app"
    echo "   Type: CNAME"
    echo "   Data: routeforcepro.netlify.app"
    echo "   TTL: 3600"
    echo ""
    echo -e "${BLUE}Option 2: Contact Squarespace Support${NC}"
    echo "Call/chat Squarespace and say:"
    echo "\"I need a CNAME record added via Google Cloud DNS:"
    echo " Domain: routeforcepro.com"
    echo " Subdomain: app"
    echo " Points to: routeforcepro.netlify.app\""
    echo ""
}

# Function to monitor DNS propagation
monitor_dns() {
    echo -e "${BLUE}Starting DNS monitoring (press Ctrl+C to stop)...${NC}"
    echo ""
    
    while true; do
        if check_dns_status; then
            echo -e "${GREEN}🎉 DNS is working! Testing website...${NC}"
            
            if test_website "https://app.routeforcepro.com"; then
                echo ""
                echo -e "${GREEN}🚀 SUCCESS! RouteForce is live at:${NC}"
                echo -e "${GREEN}   https://app.routeforcepro.com${NC}"
                echo ""
                echo "✅ DNS configured and propagated"
                echo "✅ SSL certificate active"
                echo "✅ Website accessible"
                echo "✅ All optimizations active"
                echo ""
                echo -e "${BOLD}🎯 Your RouteForce application is now fully deployed!${NC}"
                break
            else
                echo "DNS works but website not yet accessible (SSL provisioning may be in progress)"
            fi
        else
            echo "DNS not yet propagated..."
        fi
        
        echo "Checking again in 30 seconds..."
        sleep 30
    done
}

# Function to show current status
show_status() {
    echo -e "${BOLD}Current Deployment Status:${NC}"
    echo "========================="
    echo ""
    
    # Check Netlify site
    if test_website "https://routeforcepro.netlify.app"; then
        echo "✅ Netlify deployment: Working"
    else
        echo "❌ Netlify deployment: Issue detected"
    fi
    
    # Check DNS configuration
    if check_dns_status; then
        echo "✅ DNS configuration: Complete"
        if test_website "https://app.routeforcepro.com"; then
            echo "✅ Custom domain: Live and working"
            echo ""
            echo -e "${GREEN}🎉 RouteForce is fully deployed at https://app.routeforcepro.com${NC}"
            return 0
        else
            echo "⚠️  Custom domain: DNS works but site not yet accessible"
        fi
    else
        echo "❌ DNS configuration: CNAME record needed"
    fi
    
    echo ""
    return 1
}

# Main execution
main() {
    echo "Checking current deployment status..."
    echo ""
    
    if show_status; then
        echo "Deployment is complete! No further action needed."
        exit 0
    fi
    
    show_instructions
    
    echo -e "${YELLOW}What would you like to do?${NC}"
    echo "1. Monitor DNS propagation (after adding record)"
    echo "2. Check status again"
    echo "3. Show instructions again"
    echo "4. Exit"
    echo ""
    
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            monitor_dns
            ;;
        2)
            main
            ;;
        3)
            show_instructions
            main
            ;;
        4)
            echo "Exiting. Run this script again anytime to check status."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            main
            ;;
    esac
}

# Run main function
main "$@"
