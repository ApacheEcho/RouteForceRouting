#!/bin/bash

# MCP Server Status Verification Script
# Run this after restarting Claude Desktop to verify everything is working

echo "🔍 MCP Server Status Verification"
echo "=================================="
echo ""

CONFIG_FILE="$HOME/Library/Application Support/Claude/config.json"

echo "📋 Configuration Summary:"
echo "------------------------"
if [[ -f "$CONFIG_FILE" ]]; then
    SERVER_COUNT=$(grep -c '"command":' "$CONFIG_FILE")
    echo "✅ Config file exists"
    echo "✅ $SERVER_COUNT MCP servers configured"
    
    # Check for API keys
    if grep -q "YOUR_GITHUB_TOKEN" "$CONFIG_FILE"; then
        echo "⚠️  GitHub API key needs to be set"
    else
        echo "✅ GitHub API key configured"
    fi
    
    if grep -q "YOUR_CONTEXT7_API_KEY" "$CONFIG_FILE"; then
        echo "⚠️  Context7 API key not set (using free tier)"
    else
        echo "✅ Context7 API key configured"
    fi
    
    if grep -q "YOUR_BRAVE_API_KEY" "$CONFIG_FILE"; then
        echo "⚠️  Brave Search API key not set (search disabled)"
    else
        echo "✅ Brave Search API key configured"
    fi
else
    echo "❌ Config file not found!"
    exit 1
fi

echo ""
echo "🔄 Claude Desktop Status:"
echo "------------------------"
if pgrep -f "Claude" > /dev/null; then
    echo "✅ Claude Desktop is running"
    
    # Check for any MCP-related processes
    if pgrep -f "mcp" > /dev/null || pgrep -f "uvx" > /dev/null || pgrep -f "npx.*context7" > /dev/null; then
        echo "✅ MCP server processes detected"
    else
        echo "⚠️  No MCP server processes detected yet"
        echo "   (They start when Claude needs them)"
    fi
else
    echo "⚠️  Claude Desktop not running"
    echo "   Please restart Claude Desktop to activate MCP servers"
fi

echo ""
echo "🧪 Quick Test Checklist:"
echo "------------------------"
echo "After Claude Desktop restart, test these features:"
echo ""
echo "1. Model Selection Persistence:"
echo "   • Select Claude Sonnet 4 in Claude Desktop"
echo "   • Close and reopen - should remember Sonnet 4"
echo ""
echo "2. Sequential Thinking:"
echo "   • Try: 'Use sequential thinking to analyze...' "
echo "   • Should provide structured thought process"
echo ""
echo "3. Context7 Documentation:"
echo "   • Try: 'use context7 to get Next.js documentation'"
echo "   • Should fetch up-to-date docs"
echo ""
echo "4. GitHub Integration:"
echo "   • Try: 'analyze this repository structure'"
echo "   • Should access and analyze repo content"
echo ""
echo "5. Filesystem Access:"
echo "   • Try: 'list files in my home directory'"
echo "   • Should show local file system"
echo ""
echo "6. Memory Persistence:"
echo "   • Try: 'remember that I prefer TypeScript'"
echo "   • Should store and recall across sessions"
echo ""
echo "✨ If all tests pass, your MCP setup is MAXIMIZED!"
