#!/usr/bin/env python3
"""
Debug script to test export functionality
"""
import os
import sys
import io
sys.path.insert(0, '.')

print("=== DEBUG: Testing Export Functionality ===")

# Set testing environment
os.environ['TESTING'] = '1'
os.environ['FLASK_ENV'] = 'testing'

try:
    from app import create_app
    
    app = create_app('testing')
    
    with app.test_client() as client:
        print("1. Testing export endpoint with form data...")
        
        # Create sample CSV data
        sample_csv = "name,chain\nStore A,Chain A\nStore B,Chain B"
        data = {"file": (io.BytesIO(sample_csv.encode("utf-8")), "test_stores.csv")}
        
        # Test the export endpoint
        response = client.post("/export", data=data, content_type="multipart/form-data")
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Export endpoint working correctly")
            print(f"   Content-Type: {response.content_type}")
            print(f"   Data length: {len(response.data)}")
        else:
            print(f"❌ Export failed: {response.status_code}")
            if response.data:
                print(f"   Error: {response.get_data(as_text=True)}")
        
        print("\n2. Testing route generation with form data...")
        # Create fresh CSV data for second test
        sample_csv2 = "name,chain\nStore A,Chain A\nStore B,Chain B"
        data2 = {"file": (io.BytesIO(sample_csv2.encode("utf-8")), "test_stores2.csv")}
        
        response = client.post("/generate", data=data2, content_type="multipart/form-data")
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Route generation working correctly")
        else:
            print(f"❌ Route generation failed: {response.status_code}")
            if response.data:
                error_data = response.get_data(as_text=True)
                print(f"   Error: {error_data[:200]}...")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    
print("=== EXPORT DEBUG COMPLETE ===")
