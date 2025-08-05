#!/usr/bin/env python3
"""
Branch Protection Validation Script

This script validates that the branch protection setup is working correctly.
Run this script to check if all required components are in place.
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a required file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False


def check_workflow_syntax(workflow_path: str) -> bool:
    """Check if a workflow file has valid YAML syntax"""
    try:
        import yaml
        with open(workflow_path, 'r') as f:
            yaml.safe_load(f)
        print(f"✅ Valid YAML syntax: {workflow_path}")
        return True
    except ImportError:
        print(f"⚠️  Cannot validate YAML syntax (pyyaml not installed)")
        return True
    except Exception as e:
        print(f"❌ Invalid YAML syntax in {workflow_path}: {e}")
        return False


def run_syntax_check() -> bool:
    """Run syntax check on Python files"""
    try:
        result = subprocess.run(
            ['python', '-m', 'py_compile'] + [
                'app.py', 'main.py', 'routing/route_logger.py'
            ],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Python syntax check passed")
            return True
        else:
            print(f"❌ Python syntax errors found: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️  Could not run syntax check: {e}")
        return True


def check_required_workflows() -> bool:
    """Check that all required workflow files exist and are valid"""
    workflows_dir = ".github/workflows"
    required_workflows = [
        "lint.yml",
        "test.yml", 
        "branch-protection.yml",
        "ci-cd.yml"
    ]
    
    all_good = True
    
    for workflow in required_workflows:
        workflow_path = os.path.join(workflows_dir, workflow)
        if not check_file_exists(workflow_path, f"Required workflow"):
            all_good = False
        elif not check_workflow_syntax(workflow_path):
            all_good = False
    
    return all_good


def check_configuration_files() -> bool:
    """Check that configuration files are in place"""
    configs = [
        (".flake8", "Flake8 configuration"),
        (".pre-commit-config.yaml", "Pre-commit configuration"),
        ("BRANCH_PROTECTION_GUIDE.md", "Branch protection documentation"),
        ("requirements.txt", "Python requirements")
    ]
    
    all_good = True
    for file_path, description in configs:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good


def main():
    """Main validation function"""
    print("🔍 Validating Branch Protection Setup\n")
    
    # Check current directory
    if not os.path.exists("app.py"):
        print("❌ Not in project root directory")
        sys.exit(1)
    
    print("📁 Checking required files...")
    config_ok = check_configuration_files()
    
    print("\n⚙️  Checking workflows...")
    workflows_ok = check_required_workflows()
    
    print("\n🐍 Checking Python syntax...")
    syntax_ok = run_syntax_check()
    
    print("\n📋 Summary:")
    print("="*50)
    
    if config_ok and workflows_ok and syntax_ok:
        print("✅ All checks passed! Branch protection setup is ready.")
        print("\n📖 Next steps:")
        print("1. Review BRANCH_PROTECTION_GUIDE.md for GitHub configuration")
        print("2. Configure branch protection rules in GitHub repository settings")
        print("3. Test with a sample pull request")
        print("\n🔗 GitHub Settings URL:")
        print("   https://github.com/ApacheEcho/RouteForceRouting/settings/branches")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())