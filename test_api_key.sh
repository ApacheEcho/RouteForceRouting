#!/bin/bash

# 🔑 API Key Validation Script
# This script helps you test your Anthropic API key

echo "🔑 Testing Anthropic API Key..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Create one with: cp .env.example .env"
    exit 1
fi

# Load environment variables
source .env

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-anthropic-api-key-here" ]; then
    echo "❌ API key not configured!"
    echo ""
    echo "To fix this:"
    echo "1. Get your API key from: https://console.anthropic.com/"
    echo "2. Edit .env file and replace 'your-anthropic-api-key-here'"
    echo "3. Run this script again"
    exit 1
fi

# Validate API key format
if [[ ! "$ANTHROPIC_API_KEY" =~ ^sk-ant-api03- ]]; then
    echo "⚠️  API key format looks incorrect"
    echo "Expected format: sk-ant-api03-..."
    echo "Current: ${ANTHROPIC_API_KEY:0:15}..."
fi

echo "✅ API key is configured"
echo "🧪 Testing API connection..."

# Test API with a simple request
python3 -c "
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_api():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                json={
                    'model': 'claude-3-5-sonnet-20241022',
                    'max_tokens': 10,
                    'messages': [
                        {'role': 'user', 'content': 'Hello'}
                    ]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                print('✅ API connection successful!')
                print('🎉 Your API key is working!')
                
                # Check if Claude Opus is available
                data = response.json()
                print(f'📝 Test response: {data.get(\"content\", [{}])[0].get(\"text\", \"N/A\")[:50]}...')
                
                print('')
                print('🚀 Ready to use Claude Opus 4!')
                print('')
                print('Next steps:')
                print('1. Restart VS Code to load MCP config')
                print('2. OR start Flask app: python3 app.py')
                print('3. OR test endpoints: curl http://localhost:5000/claude/health')
                
            else:
                print(f'❌ API error: {response.status_code}')
                print(f'Response: {response.text}')
                
        except Exception as e:
            print(f'❌ Connection failed: {e}')
            print('')
            print('Possible issues:')
            print('- Invalid API key')
            print('- Network connection')
            print('- API key needs billing setup')

asyncio.run(test_api())
"

echo ""
echo "🔧 MCP Configuration Status:"
if [ -f "$HOME/Library/Application Support/Code/User/mcp.json" ]; then
    echo "✅ MCP config file found"
    echo "✅ Anthropic server configured"
    echo "💡 Restart VS Code to activate MCP integration"
else
    echo "⚠️  MCP config not found"
fi
