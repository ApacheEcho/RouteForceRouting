#!/usr/bin/env python3
"""
Test script for Claude Opus 4.1 integration
Tests the basic functionality without requiring a full Flask app
"""

import asyncio
import os
import sys
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

async def test_claude_integration():
    """Test the Claude Opus 4.1 integration"""
    
    print("🧪 Testing Claude Opus 4.1 Integration")
    print("=" * 50)
    
    try:
        # Import the service
        from app.claude_integration import create_claude_service
        
        print("✅ Successfully imported Claude integration module")
        
        # Create service instance
        try:
            service = create_claude_service()
            print(f"✅ Created Claude service with model: {service.config.model}")
            print(f"✅ API Key configured: {bool(service.config.api_key and service.config.api_key != 'your-anthropic-api-key-here')}")
            
            if not service.config.api_key or service.config.api_key == 'your-anthropic-api-key-here':
                print("\n⚠️  Warning: API key not configured!")
                print("Please update your .env file with a valid Anthropic API key:")
                print("ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_KEY_HERE")
                print("\nGet your API key from: https://console.anthropic.com/")
                return False
            
            # Test basic route optimization
            print("\n🔄 Testing route optimization...")
            
            sample_route_data = {
                "stops": [
                    {"address": "123 Main St, San Francisco, CA", "priority": "high", "delivery_window": "9:00-12:00"},
                    {"address": "456 Oak Ave, San Francisco, CA", "priority": "medium", "delivery_window": "13:00-17:00"},
                    {"address": "789 Pine St, San Francisco, CA", "priority": "low", "delivery_window": "flexible"}
                ],
                "constraints": {
                    "max_time": 480,  # 8 hours
                    "vehicle_capacity": 1000,  # lbs
                    "start_location": "1000 Market St, San Francisco, CA"
                },
                "current_metrics": {
                    "total_distance": 25.4,
                    "total_time": 120,
                    "fuel_cost": 15.50
                }
            }
            
            result = await service.optimize_route_with_ai(
                sample_route_data, 
                ["distance", "time", "fuel_efficiency"]
            )
            
            if result.get('success'):
                print("✅ Route optimization test successful!")
                print(f"   Model used: {result.get('model_used')}")
                print(f"   Timestamp: {result.get('timestamp')}")
                
                analysis = result.get('analysis', {})
                if isinstance(analysis, dict) and 'analysis_summary' in analysis:
                    print(f"   Summary: {analysis['analysis_summary'][:100]}...")
                else:
                    print(f"   Response length: {len(str(analysis))} characters")
                
            else:
                print(f"❌ Route optimization test failed: {result.get('error')}")
                return False
            
            # Test insights generation
            print("\n🧠 Testing insights generation...")
            
            insights_result = await service.generate_route_insights(
                "What are the key factors to consider when optimizing delivery routes in urban areas?",
                {"city": "San Francisco", "vehicle_type": "delivery_truck"}
            )
            
            if insights_result.get('success'):
                print("✅ Insights generation test successful!")
                insights = insights_result.get('insights', '')
                print(f"   Insights length: {len(insights)} characters")
                print(f"   Preview: {insights[:150]}...")
            else:
                print(f"❌ Insights generation test failed: {insights_result.get('error')}")
                return False
            
            # Clean up
            await service.close()
            print("\n✅ All tests completed successfully!")
            print("\n🎉 Claude Opus 4.1 is ready to use in your RouteForce application!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating Claude service: {str(e)}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure all dependencies are installed:")
        print("pip install httpx==0.27.0")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("\n🔧 Testing Environment Setup")
    print("=" * 30)
    
    # Check .env file
    env_file = '.env'
    if os.path.exists(env_file):
        print("✅ .env file found")
        
        # Check for API key
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key and api_key != 'your-anthropic-api-key-here':
                print("✅ Anthropic API key configured")
            else:
                print("⚠️  Anthropic API key not configured")
        except ImportError:
            print("⚠️  python-dotenv not available, checking environment variables directly")
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                print("✅ Anthropic API key found in environment")
            else:
                print("⚠️  Anthropic API key not found")
    else:
        print("⚠️  .env file not found")
    
    # Check dependencies
    try:
        import httpx
        print(f"✅ httpx installed (version: {httpx.__version__})")
    except ImportError:
        print("❌ httpx not installed")
        
    try:
        import flask
        print(f"✅ Flask installed (version: {flask.__version__})")
    except ImportError:
        print("❌ Flask not installed")

def main():
    """Main test function"""
    print(f"🚀 Claude Opus 4.1 Integration Test")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Test environment
    test_environment_setup()
    
    # Test Claude integration
    try:
        success = asyncio.run(test_claude_integration())
        
        if success:
            print("\n" + "=" * 50)
            print("🎯 NEXT STEPS:")
            print("1. Start your Flask app: python app.py")
            print("2. Test the health endpoint: curl http://localhost:5000/api/claude/health")
            print("3. Use the API endpoints or web interface")
            print("4. Check the setup guide: CLAUDE_OPUS_4_SETUP_GUIDE.md")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("❌ Tests failed. Please check the setup guide:")
            print("   CLAUDE_OPUS_4_SETUP_GUIDE.md")
            print("=" * 50)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")

if __name__ == "__main__":
    main()
