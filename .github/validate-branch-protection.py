#!/usr/bin/env python3
"""
Branch Protection Validation Script
Tests that the CI pipeline components work correctly before applying branch protection rules.
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and report success/failure"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd()
        )
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_file_exists(filepath, description):
    """Check if a required file exists"""
    print(f"🔍 {description}...")
    if os.path.exists(filepath):
        print(f"✅ {description} - EXISTS")
        return True
    else:
        print(f"❌ {description} - MISSING")
        return False


def main():
    print("🔒 Branch Protection Validation Script")
    print("=" * 50)

    all_checks_passed = True

    # Check that required files exist
    files_to_check = [
        (".github/CODEOWNERS", "CODEOWNERS file"),
        (".github/BRANCH_PROTECTION_CONFIG.md", "Branch protection documentation"),
        (".github/setup-branch-protection.sh", "Setup script"),
        (".github/workflows/ci-cd.yml", "Main CI/CD workflow"),
        (".github/workflows/lint.yml", "Lint workflow"),
        ("requirements.txt", "Python requirements"),
    ]

    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_checks_passed = False

    print("\n" + "=" * 50)
    print("🧪 Testing CI Pipeline Components")
    print("=" * 50)

    # Test code formatting
    if not run_command(
        "python -m black --check --diff .", "Code formatting check (black)"
    ):
        print("   💡 Run 'python -m black .' to fix formatting issues")
        all_checks_passed = False

    # Test critical linting
    if not run_command(
        "python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=mobile/pwa/node_modules,venv,.venv,__pycache__,migrations",
        "Critical lint check (flake8)",
    ):
        all_checks_passed = False

    # Test import capabilities
    if not run_command(
        "python -c 'import app; print(\"App imports successfully\")'",
        "App module import test",
    ):
        all_checks_passed = False

    # Test setup script is executable
    if not run_command(
        "test -x .github/setup-branch-protection.sh", "Setup script executable check"
    ):
        all_checks_passed = False

    print("\n" + "=" * 50)
    print("📋 Validation Summary")
    print("=" * 50)

    if all_checks_passed:
        print("🎉 All validation checks PASSED!")
        print("\n✅ Ready to apply branch protection rules")
        print("   Run: ./.github/setup-branch-protection.sh")
        print("\n📚 Next steps:")
        print("   1. Execute the setup script as repository admin")
        print("   2. Test with a sample pull request")
        print("   3. Verify all status checks appear and function")
        return 0
    else:
        print("⚠️  Some validation checks FAILED!")
        print("\n🔧 Please fix the above issues before applying branch protection")
        print("   Run this script again after fixes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
