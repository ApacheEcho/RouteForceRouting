#!/usr/bin/env python3

"""
Sentry Configuration Helper for RouteForce

This script helps you configure Sentry error tracking for your application.
"""

def show_sentry_setup_instructions():
    """Show instructions for getting the correct Sentry DSN."""
    
    project_id = "4509751159226368"
    
    print("🔍 Sentry Configuration for RouteForce")
    print("=" * 50)
    print(f"📋 Project ID: {project_id}")
    print()
    
    print("🔑 To get your correct Sentry DSN:")
    print("1. Go to https://sentry.io/settings/")
    print(f"2. Find your project (ID: {project_id})")
    print("3. Go to Settings → Client Keys (DSN)")
    print("4. Copy the DSN - it should look like:")
    print("   https://abcd1234@o123456.ingest.sentry.io/4509751159226368")
    print()
    
    print("🚀 Once you have the DSN, run:")
    print('gh secret set SENTRY_DSN --body="https://YOUR_KEY@o123456.ingest.sentry.io/4509751159226368"')
    print()
    
    print("📊 Sentry will provide:")
    print("• Real-time error tracking")
    print("• Performance monitoring") 
    print("• Release tracking")
    print("• User session tracking")
    print("• Integration with deployment pipeline")
    print()
    
    print("🔧 Alternative: Skip Sentry for now")
    print("Your deployment pipeline is already complete without Sentry.")
    print("You can add it later when you have the correct DSN.")

if __name__ == '__main__':
    show_sentry_setup_instructions()
