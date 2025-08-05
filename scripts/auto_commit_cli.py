#!/usr/bin/env python3
"""
Auto-commit CLI tool

Provides command line interface for managing the auto-commit service.
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.auto_commit_service import AutoCommitService


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="RouteForce Auto-Commit Service CLI")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check service status')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the auto-commit service')
    start_parser.add_argument(
        '--interval', 
        type=int, 
        default=10, 
        help='Commit interval in minutes (default: 10)'
    )
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the auto-commit service')
    
    # Force commit command
    commit_parser = subparsers.add_parser('commit', help='Force immediate commit')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test auto-commit functionality')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    service = AutoCommitService()
    
    if args.command == 'status':
        print(f"Auto-commit service status: {'running' if service.is_running else 'stopped'}")
        print(f"Repository path: {service.repo_path}")
        print(f"WIP branch: {service.wip_branch}")
        print(f"Interval: {service.interval_seconds // 60} minutes")
    
    elif args.command == 'start':
        if hasattr(args, 'interval'):
            service.interval_seconds = args.interval * 60
        service.start()
        print(f"Auto-commit service started with {args.interval}-minute intervals")
    
    elif args.command == 'stop':
        service.stop()
        print("Auto-commit service stopped")
    
    elif args.command == 'commit':
        print("Forcing immediate commit...")
        if service.force_commit_now():
            print("✅ Commit successful")
        else:
            print("❌ Commit failed")
    
    elif args.command == 'test':
        print("Testing auto-commit functionality...")
        
        # Test git status
        if service._has_git_changes():
            print("✅ Git changes detected")
        else:
            print("ℹ️  No changes detected")
        
        # Test branch management
        try:
            current_branch = service._get_current_branch()
            print(f"✅ Current branch: {current_branch}")
        except Exception as e:
            print(f"❌ Branch check failed: {e}")
        
        # Test commit message generation
        try:
            message = service._generate_smart_commit_message()
            print(f"✅ Generated commit message: {message}")
        except Exception as e:
            print(f"❌ Message generation failed: {e}")
        
        print("Test completed")


if __name__ == "__main__":
    main()