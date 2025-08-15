#!/usr/bin/env python3
"""
Auto-commit Service Demo

This script demonstrates the auto-commit service functionality.
"""

import time
import os
from app.services.auto_commit_service import AutoCommitService


def demo_auto_commit():
    """Demonstrate auto-commit functionality"""
    print("🚀 Auto-commit Service Demo")
    print("=" * 50)

    # Create service with short interval for demo
    service = AutoCommitService(interval_minutes=1)  # 1 minute for demo

    print(f"📁 Repository: {service.repo_path}")
    print(f"🌿 WIP Branch: {service.wip_branch}")
    print(f"⏰ Interval: {service.interval_seconds} seconds")

    print("\n🔍 Checking for changes...")
    if service._has_git_changes():
        print("✅ Changes detected!")

        # Generate smart commit message
        message = service._generate_smart_commit_message()
        print(f"💬 Commit message: {message}")

        # Show changed files
        changed_files = service._get_changed_files()
        print(f"📝 Changed files: {', '.join(changed_files[:5])}")
        if len(changed_files) > 5:
            print(f"    ... and {len(changed_files) - 5} more files")
    else:
        print("ℹ️  No changes detected")

    print("\n🛠️  Service Commands:")
    print(
        "python scripts/auto_commit_cli.py start    # Start auto-commit service"
    )
    print(
        "python scripts/auto_commit_cli.py stop     # Stop auto-commit service"
    )
    print("python scripts/auto_commit_cli.py status   # Check service status")
    print(
        "python scripts/auto_commit_cli.py commit   # Force immediate commit"
    )
    print("python scripts/auto_commit_cli.py test     # Test functionality")

    print("\n🔧 Environment Variables:")
    print(
        "AUTO_COMMIT_ENABLED=true/false              # Enable/disable service"
    )
    print(
        "AUTO_COMMIT_INTERVAL_MINUTES=10             # Commit interval in minutes"
    )
    print("AUTO_COMMIT_WIP_BRANCH=auto-wip             # WIP branch name")

    print("\n✨ Features:")
    print("✅ Auto-commit every 10 minutes (configurable)")
    print("✅ Smart commit messages based on file changes")
    print("✅ Push to WIP branch automatically")
    print("✅ Never lose code - everything is backed up")
    print("✅ No manual git commands needed")
    print("✅ Background service runs independently")
    print("✅ Integrates with Flask app startup")

    print("\n🎯 Issue #51 Requirements Met:")
    print("✅ Auto-commit every 10 minutes")
    print("✅ Smart commit messages")
    print("✅ Push to WIP branch")
    print("✅ Never lose a single line of code")
    print("✅ No manual git commands ever")


if __name__ == "__main__":
    demo_auto_commit()
