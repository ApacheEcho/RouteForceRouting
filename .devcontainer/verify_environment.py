#!/usr/bin/env python3
"""
GitHub Codespaces Environment Verification
Validates that the development environment is properly configured.
"""

import sys
import subprocess
import importlib


def check_python_version():
    """Check Python version is 3.12+"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 12:
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.12+ required")
        return False


def check_package(package_name, import_name=None):
    """Check if a package is available"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"   ✅ {package_name}")
        return True
    except ImportError:
        print(f"   ❌ {package_name} not available")
        return False


def check_command_line_tools():
    """Check command line development tools"""
    tools = [
        ("black", "Code formatter"),
        ("flake8", "Code linter"),
        ("pytest", "Testing framework")
    ]
    
    print("🛠️  Command Line Tools:")
    all_good = True
    
    for tool, description in tools:
        try:
            result = subprocess.run([tool, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print(f"   ✅ {tool}: {version}")
            else:
                print(f"   ❌ {tool} not working properly")
                all_good = False
        except FileNotFoundError:
            print(f"   ❌ {tool} not found")
            all_good = False
    
    return all_good


def check_flask_app():
    """Check if Flask app can be created"""
    print("🌐 Flask Application:")
    try:
        # Add current directory to Python path for app import
        import os
        import sys
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app import create_app
        app = create_app()
        print("   ✅ Flask application created successfully")
        print(f"   ✅ Debug mode: {app.config.get('DEBUG', False)}")
        return True
    except Exception as e:
        print(f"   ❌ Flask app creation failed: {e}")
        return False


def check_core_packages():
    """Check core Python packages"""
    packages = [
        ("flask", "Web framework"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data analysis"), 
        ("requests", "HTTP library"),
        ("pytest", "Testing framework"),
        ("redis", "Redis client"),
        ("geopy", "Geocoding library")
    ]
    
    print("📦 Core Packages:")
    all_good = True
    
    for package, description in packages:
        if not check_package(package):
            all_good = False
    
    return all_good


def main():
    """Run all verification checks"""
    print("🔍 GitHub Codespaces Environment Verification")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_core_packages,
        check_command_line_tools,
        check_flask_app
    ]
    
    all_passed = True
    for check in checks:
        result = check()
        all_passed = all_passed and result
        print()
    
    if all_passed:
        print("🎉 All checks passed! Your development environment is ready.")
        print("\n📋 Next Steps:")
        print("   1. Edit .env file with your Google Maps API key")
        print("   2. Run the development server: python app.py")
        print("   3. Access the app at: http://localhost:8000")
        print("\n🧪 Development Commands:")
        print("   • Run tests: python -m pytest")
        print("   • Format code: black .")
        print("   • Lint code: flake8 .")
        return 0
    else:
        print("❌ Some checks failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    exit(main())