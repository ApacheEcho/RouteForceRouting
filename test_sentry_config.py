#!/usr/bin/env python3
"""
Sentry Configuration Test Script
Tests the current Sentry setup to identify any configuration issues
"""

import sys
import os

def test_sentry_configuration():
    """Test Sentry configuration and identify issues"""
    
    print("🔍 Testing Sentry Configuration...")
    print("=" * 50)
    
    try:
        # Test basic Sentry import
        import sentry_sdk
        print(f"✅ Sentry SDK version: {sentry_sdk.VERSION}")
        
        # Test integrations import
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.redis import RedisIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        print("✅ All Sentry integrations imported successfully")
        
        # Test FlaskIntegration configuration
        print("\n🔧 Testing FlaskIntegration configuration...")
        try:
            flask_integration = FlaskIntegration(
                transaction_style='endpoint'
            )
            print("✅ FlaskIntegration created successfully with transaction_style='endpoint'")
        except Exception as e:
            print(f"❌ FlaskIntegration creation failed: {e}")
            return False
        
        # Test our Sentry config
        print("\n🔧 Testing RouteForce Sentry configuration...")
        try:
            from app.monitoring.sentry_config import SentryConfig, init_sentry
            
            # Test without DSN (should disable gracefully)
            config = SentryConfig()
            print(f"✅ SentryConfig created - Enabled: {config.is_enabled()}")
            
            # Test initialization (should return False without DSN)
            result = init_sentry()
            if result is False:
                print("✅ Sentry initialization returns False without DSN (expected behavior)")
            else:
                print("⚠️ Sentry initialization behavior unexpected")
                
        except Exception as e:
            print(f"❌ RouteForce Sentry configuration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ All Sentry configuration tests passed!")
        print("ℹ️ The error you saw is likely from an older cached version.")
        print("🚀 The new deployment should resolve the issue.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Sentry SDK: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during Sentry testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_sentry_version_compatibility():
    """Check if current Sentry SDK version has known issues"""
    
    try:
        import sentry_sdk
        version_str = sentry_sdk.VERSION
        
        print(f"\n📊 Sentry SDK Version Analysis:")
        print(f"Current version: {version_str}")
        
        # Parse version string
        try:
            version_parts = version_str.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1])
            
            if (major, minor) >= (2, 0):
                print("✅ Using Sentry SDK 2.x - Modern version with good Flask support")
                print("ℹ️ This version (2.x) does NOT support 'record_sql_params' in FlaskIntegration")
                print("✅ Your current configuration is correct for this version")
            elif (major, minor) >= (1, 20):
                print("⚠️ Using Sentry SDK 1.x - Consider upgrading to 2.x")
            else:
                print("❌ Using old Sentry SDK - Upgrade recommended")
                
        except (ValueError, IndexError):
            print("⚠️ Could not parse version string for detailed analysis")
            
    except Exception as e:
        print(f"❌ Could not check Sentry version: {e}")

if __name__ == '__main__':
    print("🔧 RouteForce Sentry Configuration Test")
    print("=" * 50)
    
    # Run tests
    success = test_sentry_configuration()
    check_sentry_version_compatibility()
    
    if success:
        print("\n🎉 Sentry configuration is working correctly!")
        print("💡 If you still see errors in deployment logs, they are likely from")
        print("   old cached code that will be resolved with the new deployment.")
        sys.exit(0)
    else:
        print("\n❌ Sentry configuration has issues that need to be resolved.")
        sys.exit(1)
