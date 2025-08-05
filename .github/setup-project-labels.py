#!/usr/bin/env python3
"""
Setup script for project automation labels.
This script ensures all required labels for project board automation exist.
"""

import os
import sys
import requests
import json

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "ApacheEcho"
REPO_NAME = "RouteForceRouting"

# Labels configuration
LABELS = [
    # Status labels
    {"name": "status:todo", "color": "d4edda", "description": "Ready to be worked on"},
    {"name": "status:in-progress", "color": "fff3cd", "description": "Currently being worked on"},
    {"name": "status:review", "color": "d1ecf1", "description": "Ready for review"},
    {"name": "status:done", "color": "c3e6cb", "description": "Completed"},
    
    # Priority labels
    {"name": "high-priority", "color": "d73a49", "description": "High priority"},
    {"name": "medium-priority", "color": "fb8500", "description": "Medium priority"},
    {"name": "low-priority", "color": "0366d6", "description": "Low priority"},
    
    # Component labels
    {"name": "component:backend", "color": "7057ff", "description": "Backend/server related"},
    {"name": "component:frontend", "color": "008672", "description": "Frontend/UI related"},
    {"name": "component:api", "color": "1d76db", "description": "API related"},
    {"name": "component:devops", "color": "f9d71c", "description": "DevOps/deployment related"},
    {"name": "component:docs", "color": "5319e7", "description": "Documentation related"},
    
    # Type labels
    {"name": "type:bug", "color": "d73a49", "description": "Bug report"},
    {"name": "type:feature", "color": "a2eeef", "description": "New feature"},
    {"name": "type:enhancement", "color": "84b6eb", "description": "Enhancement to existing feature"},
    {"name": "type:testing", "color": "d4c5f9", "description": "Testing related"},
    {"name": "type:bugfix", "color": "f85149", "description": "Bug fix (for PRs)"},
    {"name": "type:documentation", "color": "e7c847", "description": "Documentation (for PRs)"},
    {"name": "type:refactor", "color": "b794f6", "description": "Code refactoring"},
    
    # Effort labels
    {"name": "effort:small", "color": "c2e0c6", "description": "Small effort (< 4 hours)"},
    {"name": "effort:medium", "color": "fef2c0", "description": "Medium effort (4-16 hours)"},
    {"name": "effort:large", "color": "f9c2c2", "description": "Large effort (> 16 hours)"},
    
    # Special labels
    {"name": "blocked", "color": "b60205", "description": "Blocked by external dependency"},
    {"name": "has-dependency", "color": "f29513", "description": "Depends on other issues"},
    {"name": "stale", "color": "959da5", "description": "Inactive for extended period"},
]

def create_or_update_label(label):
    """Create or update a label in the repository."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/labels"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Check if label exists
    check_url = f"{url}/{label['name']}"
    response = requests.get(check_url, headers=headers)
    
    if response.status_code == 200:
        # Label exists, update it
        response = requests.patch(check_url, headers=headers, json=label)
        if response.status_code == 200:
            print(f"✅ Updated label: {label['name']}")
        else:
            print(f"❌ Failed to update label {label['name']}: {response.status_code}")
            print(f"   Response: {response.text}")
    elif response.status_code == 404:
        # Label doesn't exist, create it
        response = requests.post(url, headers=headers, json=label)
        if response.status_code == 201:
            print(f"✅ Created label: {label['name']}")
        else:
            print(f"❌ Failed to create label {label['name']}: {response.status_code}")
            print(f"   Response: {response.text}")
    else:
        print(f"❌ Error checking label {label['name']}: {response.status_code}")

def main():
    """Main function to setup project labels."""
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN environment variable is required")
        print("   Set it with: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    print(f"🚀 Setting up project automation labels for {REPO_OWNER}/{REPO_NAME}")
    print(f"   Total labels to process: {len(LABELS)}")
    print()
    
    for label in LABELS:
        create_or_update_label(label)
    
    print()
    print("🎉 Project label setup complete!")
    print("   Your project board automation is now ready to use.")
    print()
    print("Available status commands in issue comments:")
    print("   /in-progress or /start  - Move to In Progress")
    print("   /review or /ready       - Move to Review")
    print("   /done or /complete      - Close and mark as Done")
    print("   /todo or /backlog       - Move back to To Do")

if __name__ == "__main__":
    main()