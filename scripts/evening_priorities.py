#!/usr/bin/env python3
"""
Evening priorities generator for RouteForce development workflow.
Analyzes current state and generates priorities for evening development session.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=30
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""


def analyze_git_status() -> Dict[str, Any]:
    """Analyze git repository status."""
    status = {
        "branch": run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "uncommitted_changes": bool(run_git_command(["git", "status", "--porcelain"])),
        "unpushed_commits": bool(run_git_command(["git", "log", "origin/HEAD..HEAD", "--oneline"])),
        "ahead_behind": run_git_command(["git", "rev-list", "--left-right", "--count", "HEAD...origin/HEAD"]),
    }
    return status


def analyze_test_results() -> Dict[str, Any]:
    """Analyze recent test results if available."""
    test_status = {
        "last_run": None,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "coverage": None,
    }
    
    # Check for recent test artifacts
    for test_file in [".pytest_cache/README.md", "htmlcov/index.html", "coverage.xml"]:
        if os.path.exists(test_file):
            test_status["last_run"] = datetime.fromtimestamp(
                os.path.getmtime(test_file)
            ).isoformat()
            break
    
    return test_status


def scan_todo_items() -> List[str]:
    """Scan codebase for TODO items and open issues."""
    todos = []
    
    # Scan Python files for TODOs
    for py_file in Path(".").rglob("*.py"):
        if "/.git/" in str(py_file) or "__pycache__" in str(py_file):
            continue
        
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if "TODO" in line.upper() or "FIXME" in line.upper():
                        todos.append(f"{py_file}:{line_num}: {line.strip()}")
        except (UnicodeDecodeError, PermissionError):
            continue
    
    return todos[:10]  # Limit to top 10


def analyze_file_changes() -> Dict[str, Any]:
    """Analyze recent file changes."""
    recent_files = []
    
    # Get files modified in last 24 hours
    modified_files = run_git_command([
        "git", "log", "--since=24 hours ago", "--name-only", "--pretty=format:", "--"
    ])
    
    if modified_files:
        unique_files = list(set(modified_files.split("\n")))
        recent_files = [f for f in unique_files if f.strip()]
    
    return {
        "recent_files": recent_files[:10],
        "file_count": len(recent_files),
    }


def generate_evening_priorities() -> Dict[str, Any]:
    """Generate comprehensive evening development priorities."""
    timestamp = datetime.now().isoformat()
    
    priorities = {
        "generated_at": timestamp,
        "session_type": "evening_development",
        "git_status": analyze_git_status(),
        "test_status": analyze_test_results(),
        "todo_items": scan_todo_items(),
        "file_changes": analyze_file_changes(),
        "recommendations": [],
    }
    
    # Generate recommendations based on analysis
    recommendations = []
    
    if priorities["git_status"]["uncommitted_changes"]:
        recommendations.append("🔧 Review and commit pending changes")
    
    if priorities["git_status"]["unpushed_commits"]:
        recommendations.append("📤 Push local commits to remote")
    
    if not priorities["test_status"]["last_run"]:
        recommendations.append("🧪 Run test suite to ensure stability")
    
    if priorities["todo_items"]:
        recommendations.append(f"📝 Address {len(priorities['todo_items'])} TODO items")
    
    if priorities["file_changes"]["file_count"] > 5:
        recommendations.append("📋 Review recent file changes for consistency")
    
    # Add default evening priorities
    recommendations.extend([
        "🎯 Focus on high-priority features",
        "📊 Review performance metrics",
        "🔍 Code review pending PRs",
        "📚 Update documentation if needed",
    ])
    
    priorities["recommendations"] = recommendations
    
    return priorities


def save_priorities(priorities: Dict[str, Any]) -> None:
    """Save priorities to file."""
    output_file = "evening_priorities.json"
    
    with open(output_file, "w") as f:
        json.dump(priorities, f, indent=2)
    
    print(f"✅ Evening priorities saved to {output_file}")


def print_summary(priorities: Dict[str, Any]) -> None:
    """Print a human-readable summary."""
    print("\n🌅 Evening Development Priorities")
    print("=" * 40)
    print(f"Generated: {priorities['generated_at']}")
    print(f"Branch: {priorities['git_status']['branch']}")
    
    print("\n📋 Recommendations:")
    for i, rec in enumerate(priorities["recommendations"][:8], 1):
        print(f"  {i}. {rec}")
    
    if priorities["todo_items"]:
        print(f"\n📝 Found {len(priorities['todo_items'])} TODO items")
    
    print(f"\n📊 Recent activity: {priorities['file_changes']['file_count']} files modified")
    print("\n🚀 Ready for evening development session!")


def main():
    """Main function."""
    print("🔍 Analyzing development environment...")
    
    priorities = generate_evening_priorities()
    save_priorities(priorities)
    print_summary(priorities)


if __name__ == "__main__":
    main()