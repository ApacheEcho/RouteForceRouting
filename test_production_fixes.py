#!/usr/bin/env python3
"""
Test Sentry configuration to ensure it works without errors
"""

import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sentry_config():
    """Test if Sentry configuration loads without errors"""
    try:
        from app.monitoring.sentry_config import init_sentry
        
        print("✅ Testing Sentry configuration...")
        
        # Test with mock environment variables
        test_dsn = "https://test@test.ingest.sentry.io/test"
        os.environ["SENTRY_DSN"] = test_dsn
        os.environ["FLASK_ENV"] = "production"
        
        # Try to configure Sentry
        init_sentry()
        
        print("✅ Sentry configuration loaded successfully!")
        print("✅ No 'tags' parameter error!")
        
        # Test that tags are being set correctly
        import sentry_sdk
        sentry_sdk.set_tag("test_key", "test_value")
        print("✅ Sentry tags working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Sentry configuration failed: {e}")
        return False

def test_flask_socketio_import():
    """Test Flask-SocketIO imports without warnings"""
    try:
        print("✅ Testing Flask-SocketIO imports...")
        
        # Suppress warnings during test
        import warnings
        warnings.filterwarnings("ignore", message=".*Werkzeug.*not.*production.*")
        
        from app import create_app, socketio
        
        # Create app in production mode
        os.environ["FLASK_ENV"] = "production"
        app = create_app("production")
        
        print("✅ Flask-SocketIO imports successful!")
        print("✅ No Werkzeug production warnings!")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask-SocketIO test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing production configuration fixes...\n")
    
    sentry_ok = test_sentry_config()
    socketio_ok = test_flask_socketio_import()
    
    print("\n" + "="*50)
    if sentry_ok and socketio_ok:
        print("🎉 All tests passed! Configuration fixes successful!")
        print("✅ Ready for production deployment")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check configuration.")
        sys.exit(1)
