#!/usr/bin/env python3
"""
Debug script to test core functionality step by step
"""
import os
import sys
sys.path.insert(0, '.')

print("=== DEBUG: Testing Core Components ===")

# Set testing environment
os.environ['TESTING'] = '1'
os.environ['FLASK_ENV'] = 'testing'

try:
    print("1. Testing basic imports...")
    from flask import Flask
    print("✅ Flask import successful")
    
    from app import create_app
    print("✅ App factory import successful")
    
    # Create test app
    print("2. Creating test app...")
    app = create_app('testing')
    print("✅ App creation successful")
    
    # Test client
    print("3. Testing client creation...")
    with app.test_client() as client:
        print("✅ Test client created")
        
        # Test basic route
        print("4. Testing basic route...")
        response = client.get('/')
        print(f"✅ Index route status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Route works - checking content...")
            data = response.get_data(as_text=True)
            
            # Check key content
            if "RouteForce Routing" in data:
                print("✅ Title found")
            else:
                print("❌ Title missing")
            
            if "<h1>" in data:
                print("✅ H1 tag found")
            else:
                print("❌ H1 tag missing")
                
            if "form" in data:
                print("✅ Form found")
            else:
                print("❌ Form missing")
        else:
            print(f"❌ Route failed with status: {response.status_code}")
    
    print("🎉 Basic functionality test completed successfully!")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    
print("=== DEBUG COMPLETE ===")
