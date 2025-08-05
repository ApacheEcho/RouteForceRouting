#!/usr/bin/env python3
"""
Test script to validate Dependabot configuration setup.
Verifies that all configured directories and files exist.
"""

import os
import yaml
import sys
from pathlib import Path


def test_dependabot_config():
    """Test that Dependabot configuration is valid and all directories exist."""
    config_path = Path(".github/dependabot.yml")
    
    # Check if dependabot.yml exists
    if not config_path.exists():
        print("❌ .github/dependabot.yml not found")
        return False
    
    print("✅ .github/dependabot.yml exists")
    
    # Load and parse the configuration
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Failed to parse dependabot.yml: {e}")
        return False
    
    print("✅ dependabot.yml is valid YAML")
    
    # Check all configured directories
    updates = config.get("updates", [])
    if not updates:
        print("❌ No updates configured")
        return False
    
    print(f"✅ Found {len(updates)} update configurations")
    
    missing_dirs = []
    for update in updates:
        ecosystem = update.get("package-ecosystem")
        directory = update.get("directory", "/")
        
        # Convert relative directory to absolute path
        if directory == "/":
            dir_path = Path(".")
        else:
            dir_path = Path(directory.lstrip("/"))
        
        print(f"🔍 Checking {ecosystem} in {directory}")
        
        if ecosystem == "pip":
            # Check for requirements.txt
            req_file = dir_path / "requirements.txt"
            if req_file.exists():
                print(f"  ✅ Found requirements.txt")
            else:
                print(f"  ❌ Missing requirements.txt")
                missing_dirs.append(f"{directory}/requirements.txt")
        
        elif ecosystem == "npm":
            # Check for package.json
            pkg_file = dir_path / "package.json"
            if pkg_file.exists():
                print(f"  ✅ Found package.json")
            else:
                print(f"  ❌ Missing package.json")
                missing_dirs.append(f"{directory}/package.json")
        
        elif ecosystem == "docker":
            # Check for Dockerfile or docker-compose files
            dockerfile = dir_path / "Dockerfile"
            docker_compose = dir_path / "docker-compose.yml"
            if dockerfile.exists() or docker_compose.exists():
                print(f"  ✅ Found Docker configuration")
            else:
                print(f"  ⚠️  No Dockerfile or docker-compose.yml found (may be in subdirectories)")
        
        elif ecosystem == "github-actions":
            # Check for .github/workflows directory
            workflows_dir = Path(".github/workflows")
            if workflows_dir.exists() and any(workflows_dir.iterdir()):
                print(f"  ✅ Found GitHub Actions workflows")
            else:
                print(f"  ❌ Missing GitHub Actions workflows")
                missing_dirs.append(".github/workflows")
    
    if missing_dirs:
        print(f"\n❌ Missing dependencies or directories: {missing_dirs}")
        return False
    
    print("\n✅ All Dependabot configurations are valid!")
    return True


def test_workflow_file():
    """Test that the dependabot auto-merge workflow exists and is valid."""
    workflow_path = Path(".github/workflows/dependabot-auto-merge.yml")
    
    if not workflow_path.exists():
        print("❌ dependabot-auto-merge.yml workflow not found")
        return False
    
    print("✅ dependabot-auto-merge.yml workflow exists")
    
    try:
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        print("✅ dependabot-auto-merge.yml is valid YAML")
        
        # Check for required jobs
        jobs = workflow.get("jobs", {})
        if "auto-merge" in jobs or "test-python" in jobs:
            print("✅ Auto-merge jobs configured")
        else:
            print("⚠️  Auto-merge job configuration may need review")
            
    except Exception as e:
        print(f"❌ Failed to parse workflow: {e}")
        return False
    
    return True


def main():
    """Main test function."""
    print("🔍 Testing Dependabot setup for RouteForceRouting")
    print("=" * 50)
    
    success = True
    
    # Test dependabot configuration
    success &= test_dependabot_config()
    print()
    
    # Test workflow file
    success &= test_workflow_file()
    print()
    
    if success:
        print("🎉 All Dependabot setup tests passed!")
        return 0
    else:
        print("❌ Some Dependabot setup tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())