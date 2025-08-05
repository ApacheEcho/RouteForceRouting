#!/usr/bin/env python3
"""
Validation script for RouteForce Routing development environment
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists and report the result."""
    if os.path.exists(path):
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description} missing: {path}")
        return False


def check_devcontainer_config():
    """Validate devcontainer configuration."""
    print("🔍 Checking devcontainer configuration...")
    
    results = []
    
    # Check main files
    results.append(check_file_exists(".devcontainer/devcontainer.json", "DevContainer config"))
    results.append(check_file_exists(".devcontainer/Dockerfile", "DevContainer Dockerfile"))
    results.append(check_file_exists(".devcontainer/setup.sh", "Setup script"))
    results.append(check_file_exists(".devcontainer/README.md", "DevContainer documentation"))
    
    # Validate JSON syntax
    try:
        with open(".devcontainer/devcontainer.json", "r") as f:
            config = json.load(f)
        print("✅ DevContainer JSON is valid")
        
        # Check key configurations
        required_keys = ["name", "dockerFile", "customizations", "forwardPorts"]
        for key in required_keys:
            if key in config:
                print(f"✅ DevContainer has {key} configuration")
            else:
                print(f"⚠️  DevContainer missing {key} configuration")
                results.append(False)
                
    except json.JSONDecodeError as e:
        print(f"❌ DevContainer JSON is invalid: {e}")
        results.append(False)
    except FileNotFoundError:
        print("❌ DevContainer JSON not found")
        results.append(False)
    
    return all(results)


def check_python_environment():
    """Check Python environment and dependencies."""
    print("\n🐍 Checking Python environment...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check key dependencies
    required_packages = [
        "flask", "pytest", "black", "flake8", "isort", 
        "requests", "pandas", "numpy"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Package available: {package}")
        except ImportError:
            print(f"❌ Package missing: {package}")
            missing_packages.append(package)
    
    return len(missing_packages) == 0


def check_app_startup():
    """Test that the Flask app can start."""
    print("\n🚀 Testing app startup...")
    
    try:
        # Add current directory to path for app imports
        import sys
        sys.path.insert(0, os.getcwd())
        
        from app import create_app
        app = create_app("development")
        print("✅ Flask app creates successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False


def main():
    """Main validation function."""
    print("🧪 RouteForce Routing DevContainer Validation")
    print("=" * 50)
    
    checks = [
        ("DevContainer Configuration", check_devcontainer_config),
        ("Python Environment", check_python_environment),
        ("App Startup", check_app_startup),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🏁 Validation Summary")
    print("=" * 50)
    
    if all(results):
        print("🎉 All checks passed! DevContainer is ready for development.")
        print("\n📋 Next steps:")
        print("1. Open the project in VS Code")
        print("2. Select 'Reopen in Container' when prompted")
        print("3. Update .env with your Google Maps API key")
        print("4. Start developing!")
        return 0
    else:
        failed_count = len([r for r in results if not r])
        print(f"⚠️  {failed_count} checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())