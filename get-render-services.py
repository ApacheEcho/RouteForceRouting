#!/usr/bin/env python3

import os
import requests
import json
from typing import Dict, Any

def get_render_services():
    """Get all Render services and display their details."""
    api_key = os.getenv('RENDER_API_KEY')
    if not api_key:
        print("❌ RENDER_API_KEY not set. Export it or add to your environment (never commit real keys).")
        return None
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    try:
        print("🔍 Fetching your Render services...")
        response = requests.get('https://api.render.com/v1/services', headers=headers)
        response.raise_for_status()
        
        services = response.json()
        
        if not services:
            print("📋 No services found. You'll need to create services in your Render dashboard.")
            print("🔗 Go to: https://dashboard.render.com/")
            return
        
        print(f"\n✅ Found {len(services)} Render service(s):")
        print("-" * 80)
        
        for i, service in enumerate(services, 1):
            service_id = service.get('id', 'unknown')
            name = service.get('name', 'Unknown')
            service_type = service.get('type', 'unknown')
            status = service.get('serviceDetails', {}).get('status', 'unknown')
            created_at = service.get('createdAt', 'unknown')
            
            print(f"\n🏷️  Service #{i}")
            print(f"   Name: {name}")
            print(f"   ID: {service_id}")
            print(f"   Type: {service_type}")
            print(f"   Status: {status}")
            print(f"   Created: {created_at}")
            
            # For web services, show the URL
            if service_type == 'web_service':
                service_url = service.get('serviceDetails', {}).get('url', 'Not available')
                print(f"   URL: {service_url}")
        
        print("\n" + "=" * 80)
        print("📝 To use these services in your deployment:")
        print("   • Copy the Service ID for staging/production")
        print("   • Update your GitHub repository secrets:")
        
        for i, service in enumerate(services, 1):
            service_id = service.get('id')
            name = service.get('name', f'service-{i}')
            print(f"   gh secret set RENDER_STAGING_SERVICE_ID --body=\"{service_id}\"")
            if len(services) > 1:
                print(f"   gh secret set RENDER_PRODUCTION_SERVICE_ID --body=\"{service_id}\"")
        
        print("\n🚀 Next steps:")
        print("   1. Set the service IDs as GitHub secrets (commands above)")
        print("   2. Test deployment: ./scripts/deploy-render.sh deploy --environment staging --dry-run")
        print("   3. Follow RENDER_DEPLOYMENT_CHECKLIST.md for complete setup")
        
        return services
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Render services: {e}")
        if "401" in str(e):
            print("🔑 Check your API key - it may be invalid or expired")
        elif "403" in str(e):
            print("🚫 API key doesn't have sufficient permissions")
        return None

if __name__ == '__main__':
    get_render_services()
