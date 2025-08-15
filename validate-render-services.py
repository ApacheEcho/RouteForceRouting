#!/usr/bin/env python3

import os
import requests
import sys
from typing import Dict, Any


def validate_render_services():
    """Validate Render services are properly configured."""
    api_key = os.getenv("RENDER_API_KEY")
    if not api_key:
        print("❌ RENDER_API_KEY not set")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        # Get all services
        response = requests.get(
            "https://api.render.com/v1/services", headers=headers
        )
        response.raise_for_status()

        services = response.json()
        print(f"✅ Found {len(services)} Render services")

        for service in services:
            name = service.get("name", "Unknown")
            status = service.get("serviceDetails", {}).get("status", "unknown")
            service_type = service.get("type", "unknown")
            print(f"  • {name} ({service_type}) - {status}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Error validating Render services: {e}")
        return False


if __name__ == "__main__":
    if validate_render_services():
        print("✅ Render services validation passed")
        sys.exit(0)
    else:
        print("❌ Render services validation failed")
        sys.exit(1)
