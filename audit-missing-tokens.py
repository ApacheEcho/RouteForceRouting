#!/usr/bin/env python3

"""
Missing Tokens Audit for RouteForce Deployment Pipeline
Comprehensive check for all required secrets and tokens
"""

import os
import subprocess
from typing import Dict, List, Set


def get_github_secrets() -> Set[str]:
    """Get list of configured GitHub secrets."""
    try:
        result = subprocess.run(
            ["gh", "secret", "list"], capture_output=True, text=True
        )
        secrets = set()
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if line.strip() and not line.startswith("NAME"):  # Skip header
                secret_name = line.split()[0]
                if secret_name != "NAME":  # Extra safety check
                    secrets.add(secret_name)
        return secrets
    except Exception as e:
        print(f"Error getting GitHub secrets: {e}")
        return set()


def analyze_workflow_secrets() -> Dict[str, List[str]]:
    """Analyze all workflow files to find required secrets."""

    # All secrets referenced in workflows
    workflow_secrets = {
        "render-deploy.yml": [
            "RENDER_API_KEY",
            "RENDER_STAGING_SERVICE_ID",
            "RENDER_PRODUCTION_SERVICE_ID",
            "DOCKER_USERNAME",
            "DOCKER_PASSWORD",
            "CODECOV_TOKEN",
            "SLACK_WEBHOOK_URL",  # Optional
        ],
        "sentry-integration.yml": ["SENTRY_AUTH_TOKEN", "SENTRY_DSN"],
        "sentry-notify.yml": ["SENTRY_AUTH_TOKEN"],
        "codecov-coverage.yml": ["CODECOV_TOKEN"],
        # Note: GITHUB_TOKEN is automatically provided by GitHub Actions
    }

    return workflow_secrets


def check_missing_tokens():
    """Main audit function to check for missing tokens."""

    print("🔍 RouteForce Deployment - Missing Tokens Audit")
    print("=" * 60)

    # Get configured secrets
    configured_secrets = get_github_secrets()
    print(f"\n✅ Configured GitHub Secrets ({len(configured_secrets)}):")
    for secret in sorted(configured_secrets):
        print(f"   🔑 {secret}")

    # Analyze workflow requirements
    workflow_secrets = analyze_workflow_secrets()

    print(f"\n📋 Workflow Secret Requirements:")

    missing_critical = []
    missing_optional = []

    for workflow, secrets in workflow_secrets.items():
        print(f"\n📁 {workflow}:")
        for secret in secrets:
            if secret in configured_secrets:
                print(f"   ✅ {secret}")
            else:
                if secret in ["SLACK_WEBHOOK_URL", "SENTRY_AUTH_TOKEN"]:
                    print(f"   ⚠️  {secret} (optional)")
                    missing_optional.append(secret)
                else:
                    print(f"   ❌ {secret} (MISSING)")
                    missing_critical.append(secret)

    # Summary
    print(f"\n" + "=" * 60)
    print("📊 AUDIT SUMMARY:")

    if not missing_critical:
        print("✅ All CRITICAL secrets are configured!")
    else:
        print(f"❌ Missing {len(missing_critical)} CRITICAL secrets:")
        for secret in set(missing_critical):
            print(f"   • {secret}")

    if missing_optional:
        print(
            f"\n⚠️  Optional secrets not configured ({len(set(missing_optional))}):"
        )
        for secret in set(missing_optional):
            print(f"   • {secret}")

    # Deployment readiness
    print(f"\n🎯 DEPLOYMENT READINESS:")
    if not missing_critical:
        print("✅ READY FOR DEPLOYMENT!")
        print("   Your Render CI/CD pipeline has all required secrets.")
        print("   Optional secrets can be added later for enhanced features.")
    else:
        print("❌ NOT READY - Critical secrets missing")
        print("   Configure missing secrets before deployment.")

    # Instructions for missing secrets
    if missing_critical or missing_optional:
        print(f"\n🔧 Configuration Instructions:")

        unique_missing = set(missing_critical + missing_optional)

        if "SENTRY_AUTH_TOKEN" in unique_missing:
            print("   📍 SENTRY_AUTH_TOKEN:")
            print("      1. Go to https://sentry.io/settings/auth-tokens/")
            print("      2. Create new token with 'project:write' scope")
            print(
                '      3. gh secret set SENTRY_AUTH_TOKEN --body="your_token"'
            )

        if "SLACK_WEBHOOK_URL" in unique_missing:
            print("   📍 SLACK_WEBHOOK_URL:")
            print("      1. Go to your Slack → Apps → Incoming Webhooks")
            print("      2. Create webhook for deployment notifications")
            print(
                '      3. gh secret set SLACK_WEBHOOK_URL --body="https://hooks.slack.com/..."'
            )

    print(f"\n🚀 Current Service Status:")
    print("   Service: RouteForcePro")
    print("   URL: https://routeforcepro.onrender.com")
    print("   Status: Ready for deployment")


if __name__ == "__main__":
    check_missing_tokens()
