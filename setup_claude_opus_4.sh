#!/bin/bash

# 🚀 Claude Opus 4 Setup Script
# This script helps you set up Claude Opus 4 access quickly

echo "🚀 Setting up Claude Opus 4 access..."

# Check if API key is already set
if grep -q "your-anthropic-api-key-here" .env; then
    echo ""
    echo "⚠️  You need to add your Anthropic API key!"
    echo ""
    echo "1. Get your FREE API key: https://console.anthropic.com/"
    echo "2. Edit .env file and replace 'your-anthropic-api-key-here' with your actual key"
    echo ""
    echo "Want to edit it now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ${EDITOR:-vim} .env
    fi
else
    echo "✅ API key found in .env file"
fi

echo ""
echo "🔧 Testing Claude API connection..."

# Test the API
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key and api_key != 'your-anthropic-api-key-here':
    print('✅ API key is configured')
    print('🚀 Starting Flask app to test Claude integration...')
else:
    print('❌ API key not configured. Please update .env file.')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎯 Ready to test! Run these commands:"
    echo ""
    echo "# Start the server:"
    echo "python app.py"
    echo ""
    echo "# Test Claude Opus 4 (in another terminal):"
    echo "curl -X POST http://localhost:5000/claude/chat -H 'Content-Type: application/json' -d '{\"message\": \"Hello Claude Opus 4!\"}'"
    echo ""
    echo "🎉 You now have Claude Opus 4 access without a subscription!"
fi
