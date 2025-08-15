#!/usr/bin/env python3

import os
import requests
import json
from typing import Dict, Any


def check_specific_service(service_id: str):
    """Check details of a specific Render service by ID."""
    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        print(
            "❌ RENDER_API_KEY not set. Export it or add to your environment (do not commit)."
        )
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        print(f"🔍 Checking Render service: {service_id}")

        # Get specific service details
        response = requests.get(
            f"https://api.render.com/v1/services/{service_id}", headers=headers
        )
        response.raise_for_status()

        service = response.json()

        print("\n✅ Service Details:")
        print("-" * 60)
        print(f"🏷️  Name: {service.get('name', 'Unknown')}")
        print(f"🆔 ID: {service.get('id', 'Unknown')}")
        print(f"🔧 Type: {service.get('type', 'Unknown')}")
        print(f"🌐 Environment: {service.get('env', 'Unknown')}")
        print(f"📅 Created: {service.get('createdAt', 'Unknown')}")
        print(f"🔄 Updated: {service.get('updatedAt', 'Unknown')}")

        # Service details
        service_details = service.get("serviceDetails", {})
        if service_details:
            print("\n📊 Service Status:")
            print(f"   Status: {service_details.get('status', 'Unknown')}")
            print(
                f"   Deploy Status: {service_details.get('deployStatus', 'Unknown')}"
            )
            if "url" in service_details:
                print(f"   URL: {service_details['url']}")

        # Recent deploys
        try:
            deploys_response = requests.get(
                f"https://api.render.com/v1/services/{service_id}/deploys",
                headers=headers,
            )
            if deploys_response.status_code == 200:
                deploys = deploys_response.json()
                if deploys:
                    print(f"\n🚀 Recent Deployments ({len(deploys)} found):")
                    for i, deploy in enumerate(deploys[:3]):  # Show last 3
                        status = deploy.get("status", "Unknown")
                        created = deploy.get("createdAt", "Unknown")
                        print(f"   {i+1}. {status} - {created}")
                else:
                    print("\n🚀 No deployments found")
        except Exception:
            print("\n⚠️  Could not fetch deployment history")

        print("\n" + "=" * 60)
        print("✅ Service is configured and accessible via API")

        return service

    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking service {service_id}: {e}")
        if "404" in str(e):
            print("🔍 Service ID not found - check if it's correct")
        elif "401" in str(e):
            print("🔑 Check your API key")
        elif "403" in str(e):
            print("🚫 API key doesn't have access to this service")
        return None


if __name__ == "__main__":
    service_id = os.getenv("RENDER_SERVICE_ID", "")
    if not service_id:
        print("⚠️  Set RENDER_SERVICE_ID to check a specific service.")
    else:
        check_specific_service(service_id)
