# Claude Opus 4.1 Activation Guide for RouteForce

This guide will help you activate Claude Opus 4.1 in your RouteForce routing application. You now have multiple ways to access and use Claude Opus 4.1:

## 🚀 Quick Start

### 1. Get Your Anthropic API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to "API Keys" in the bottom left corner
4. Click "Create Key" and copy your API key

### 2. Configure Your Environment

1. Open your `.env` file in the RouteForce directory
2. Replace `your-anthropic-api-key-here` with your actual API key:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE
   ```

### 3. Install Dependencies

Run this command to install the required HTTP client:
```bash
pip install httpx==0.27.0
```

### 4. Test Your Setup

Start your Flask application and test the Claude endpoints:
```bash
python app.py
```

Test the health endpoint:
```bash
curl http://localhost:5000/api/claude/health
```

## 🔧 Available Integration Methods

### Method 1: Direct API Integration (Recommended for Apps)

Your RouteForce application now has these Claude Opus 4.1 endpoints:

- **Health Check**: `GET /api/claude/health`
- **Route Optimization**: `POST /api/claude/optimize-route`
- **Performance Analysis**: `POST /api/claude/analyze-performance`  
- **AI Insights**: `POST /api/claude/insights`
- **Chat Interface**: `POST /api/claude/chat`
- **Model List**: `GET /api/claude/models`

#### Example: Route Optimization

```bash
curl -X POST http://localhost:5000/api/claude/optimize-route \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "route_data": {
      "stops": [
        {"address": "123 Main St", "priority": "high"},
        {"address": "456 Oak Ave", "priority": "medium"}
      ],
      "constraints": {
        "max_time": 480,
        "vehicle_capacity": 1000
      }
    },
    "optimization_goals": ["distance", "time", "fuel_efficiency"]
  }'
```

#### Example: AI Insights

```bash
curl -X POST http://localhost:5000/api/claude/insights \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "What are the best practices for optimizing delivery routes in urban areas?",
    "context_data": {
      "city": "San Francisco",
      "vehicle_type": "delivery_truck"
    }
  }'
```

### Method 2: Claude Desktop (MCP Integration)

For development and testing:

1. Run the MCP setup script:
   ```bash
   ./setup_mcp_api_keys.sh
   ```

2. Enter your Anthropic API key when prompted

3. Restart Claude Desktop

4. You can now use Claude Opus 4.1 directly in Claude Desktop with access to your RouteForce project files

### Method 3: Claude.ai Web Interface

For premium users:

1. Visit [claude.ai](https://claude.ai)
2. Upgrade to Max, Team, or Enterprise plan
3. Select "Claude Opus 4.1" from the model dropdown
4. Start using Claude Opus 4.1 directly in the web interface

### Method 4: Cloud Providers

#### AWS Bedrock
```python
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
response = bedrock.invoke_model(
    modelId='anthropic.claude-opus-4-1-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": "Optimize this route..."}]
    })
)
```

#### Google Cloud Vertex AI
```python
from vertexai.generative_models import GenerativeModel

model = GenerativeModel("claude-opus-4-1")
response = model.generate_content("Optimize this delivery route...")
```

## 🎯 Claude Opus 4.1 Capabilities

### Advanced Route Optimization
- Multi-objective optimization (time, distance, fuel, cost)
- Real-time traffic analysis
- Vehicle capacity constraints
- Driver skill level considerations
- Customer priority weighting

### Intelligent Performance Analysis
- Historical route performance evaluation
- Pattern recognition in delivery data
- Efficiency trend identification
- Cost optimization recommendations

### Natural Language Insights
- Ask questions about your routing data in plain English
- Get actionable recommendations
- Understand complex logistics scenarios
- Strategic planning assistance

## 🔒 Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for production**
3. **Rotate API keys regularly**
4. **Monitor API usage and costs**
5. **Use HTTPS in production**

## 💰 Pricing Information

Claude Opus 4.1 pricing (as of August 2025):
- **Input tokens**: $15 per million tokens
- **Output tokens**: $75 per million tokens
- **Prompt caching**: Up to 90% cost savings
- **Batch processing**: 50% cost savings

Typical usage for route optimization:
- Simple route (~500 tokens): ~$0.01-0.04
- Complex analysis (~2000 tokens): ~$0.05-0.15

## 🚦 Usage Examples

### Python Integration

```python
import asyncio
from app.claude_integration import create_claude_service

async def optimize_my_route():
    service = create_claude_service()
    
    route_data = {
        "stops": [
            {"address": "123 Main St", "priority": "high"},
            {"address": "456 Oak Ave", "priority": "medium"}
        ],
        "constraints": {"max_time": 480}
    }
    
    result = await service.optimize_route_with_ai(route_data)
    print(result)
    
    await service.close()

# Run the async function
asyncio.run(optimize_my_route())
```

### JavaScript/Frontend Integration

```javascript
async function optimizeRoute(routeData) {
  const response = await fetch('/api/claude/optimize-route', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      route_data: routeData,
      optimization_goals: ['distance', 'time', 'fuel_efficiency']
    })
  });
  
  const result = await response.json();
  return result;
}
```

## 🔍 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your API key starts with `sk-ant-api03-`
2. **Rate Limits**: Claude Opus 4.1 has usage limits; upgrade your plan if needed
3. **Timeout Errors**: Increase the timeout value in your `.env` file
4. **Network Issues**: Check your internet connection and firewall settings

### Debug Commands

```bash
# Test API connectivity
curl -H "X-API-Key: your-key" -H "anthropic-version: 2023-06-01" \
  https://api.anthropic.com/v1/messages

# Check your API key status
python -c "
from app.claude_integration import create_claude_service
service = create_claude_service()
print(f'Model: {service.config.model}')
print(f'API Key configured: {bool(service.config.api_key)}')
"
```

## 📚 Next Steps

1. **Test the integration** with the provided examples
2. **Explore the API endpoints** to understand the capabilities
3. **Integrate with your existing workflows**
4. **Monitor usage and costs** in the Anthropic Console
5. **Scale up** to production when ready

## 🎉 You're All Set!

Claude Opus 4.1 is now activated in your RouteForce application! You can use it for:
- Intelligent route optimization
- Performance analysis and insights
- Natural language queries about your data
- Strategic logistics planning

Happy routing! 🚛✨
