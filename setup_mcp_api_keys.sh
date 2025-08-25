#!/bin/bash

# MCP Server API Keys Setup Script
# This script helps you configure API keys for your maximized MCP servers

echo "🔧 MCP Server API Keys Setup"
echo "============================"
echo ""

CONFIG_FILE="$HOME/Library/Application Support/Claude/config.json"

echo "📍 Current config location: $CONFIG_FILE"
echo ""

# Function to update API key in config
update_api_key() {
    local key_name=$1
    local key_value=$2
    local temp_file=$(mktemp)
    
    if [[ -f "$CONFIG_FILE" ]]; then
        # Use sed to replace the placeholder with actual key
        sed "s|$key_name|$key_value|g" "$CONFIG_FILE" > "$temp_file"
        mv "$temp_file" "$CONFIG_FILE"
        echo "✅ Updated $key_name"
    else
        echo "❌ Config file not found!"
        exit 1
    fi
}

echo "🔑 API Key Setup Guide:"
echo ""

echo "1. CONTEXT7 API KEY (Recommended - Higher rate limits)"
echo "   • Visit: https://context7.com/dashboard"
echo "   • Create account and get your API key"
read -p "   • Enter your Context7 API key (or press Enter to skip): " CONTEXT7_KEY

if [[ ! -z "$CONTEXT7_KEY" ]]; then
    update_api_key "YOUR_CONTEXT7_API_KEY" "$CONTEXT7_KEY"
else
    echo "   ⏭️  Skipped - Using free tier"
fi

echo ""
echo "2. GITHUB PERSONAL ACCESS TOKEN (For repository access)"
echo "   • Visit: https://github.com/settings/tokens"
echo "   • Create token with 'repo' and 'read:org' permissions"
read -p "   • Enter your GitHub token (or press Enter to skip): " GITHUB_TOKEN

if [[ ! -z "$GITHUB_TOKEN" ]]; then
    update_api_key "YOUR_GITHUB_TOKEN" "$GITHUB_TOKEN"
else
    echo "   ⏭️  Skipped - GitHub server will be disabled"
fi

echo ""
echo "3. BRAVE SEARCH API KEY (Optional - For web search)"
echo "   • Visit: https://api.search.brave.com/"
echo "   • Sign up for free API access"
read -p "   • Enter your Brave API key (or press Enter to skip): " BRAVE_KEY

if [[ ! -z "$BRAVE_KEY" ]]; then
    update_api_key "YOUR_BRAVE_API_KEY" "$BRAVE_KEY"
else
    echo "   ⏭️  Skipped - Web search will be disabled"
fi

echo ""
echo "🎯 SETUP COMPLETE!"
echo ""
echo "Next steps:"
echo "1. Restart Claude Desktop"
echo "2. Test model selection persistence"
echo "3. Try using enhanced MCP servers!"
echo ""
echo "✨ Your MCP servers are now maximized and configured!"
