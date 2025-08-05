#!/usr/bin/env python3
"""
Test script for project automation workflows.
Validates the automation logic without requiring GitHub API calls.
"""

import re
import json

# Simulated issue data for testing
TEST_ISSUES = [
    {
        "title": "Fix critical API bug in routing service",
        "body": "The routing endpoint is returning 500 errors",
        "labels": []
    },
    {
        "title": "Add new frontend dashboard component",
        "body": "Create a simple dashboard interface for users",
        "labels": []
    },
    {
        "title": "Improve backend performance optimization",
        "body": "Complex refactoring of the core algorithm to handle large datasets",
        "labels": []
    },
    {
        "title": "Quick documentation update for API",
        "body": "Simple fix to the README file",
        "labels": []
    },
    {
        "title": "Deploy Docker container to production",
        "body": "Set up the deployment pipeline for the new release",
        "labels": []
    }
]

def detect_component_labels(title, body):
    """Test component detection logic."""
    title_lower = title.lower()
    body_lower = body.lower()
    labels = []
    
    if 'api' in title_lower or 'endpoint' in body_lower or 'route' in title_lower:
        labels.append('component:api')
    if 'frontend' in title_lower or 'ui' in body_lower or 'interface' in body_lower:
        labels.append('component:frontend')
    if 'backend' in title_lower or 'server' in body_lower or 'database' in body_lower:
        labels.append('component:backend')
    if 'deploy' in title_lower or 'docker' in body_lower or 'ci/cd' in body_lower:
        labels.append('component:devops')
    if 'doc' in title_lower or 'documentation' in body_lower or 'readme' in body_lower:
        labels.append('component:docs')
    
    return labels

def detect_type_labels(title, body):
    """Test type detection logic."""
    title_lower = title.lower()
    body_lower = body.lower()
    labels = []
    
    if 'bug' in title_lower or 'error' in title_lower or 'fix' in title_lower:
        labels.append('type:bug')
    if 'feature' in title_lower or 'enhancement' in title_lower or 'add' in title_lower:
        labels.append('type:feature')
    if 'refactor' in title_lower or 'improve' in title_lower or 'optimize' in title_lower:
        labels.append('type:enhancement')
    if 'test' in title_lower or 'testing' in body_lower or 'spec' in title_lower:
        labels.append('type:testing')
    
    return labels

def detect_priority(title, body):
    """Test priority detection logic."""
    title_lower = title.lower()
    body_lower = body.lower()
    
    high_priority_keywords = ['urgent', 'critical', 'blocking', 'hotfix', 'security']
    medium_priority_keywords = ['bug', 'issue', 'problem', 'enhancement']
    
    if any(keyword in title_lower or keyword in body_lower for keyword in high_priority_keywords):
        return 'high-priority'
    elif any(keyword in title_lower or keyword in body_lower for keyword in medium_priority_keywords):
        return 'medium-priority'
    else:
        return 'low-priority'

def detect_effort(title, body):
    """Test effort estimation logic."""
    title_lower = title.lower()
    body_lower = body.lower()
    
    if 'quick' in title_lower or 'small' in title_lower or 'simple' in body_lower:
        return 'effort:small'
    elif 'complex' in title_lower or 'major' in title_lower or 'significant' in body_lower:
        return 'effort:large'
    else:
        return 'effort:medium'

def test_comment_commands():
    """Test comment command detection."""
    test_comments = [
        "/in-progress starting work on this",
        "looks good /review please",
        "this is /done",
        "move back to /todo",
        "can someone /start this task?"
    ]
    
    command_patterns = {
        r'/in-progress|/start': 'in-progress',
        r'/review|/ready': 'review',
        r'/done|/complete': 'done',
        r'/todo|/backlog': 'todo'
    }
    
    results = []
    for comment in test_comments:
        comment_lower = comment.lower()
        detected_command = None
        
        for pattern, command in command_patterns.items():
            if re.search(pattern, comment_lower):
                detected_command = command
                break
        
        results.append({
            'comment': comment,
            'detected_command': detected_command
        })
    
    return results

def run_automation_tests():
    """Run all automation tests."""
    print("🧪 Testing Project Automation Logic")
    print("=" * 50)
    
    # Test issue processing
    print("\n📋 Testing Issue Processing:")
    for i, issue in enumerate(TEST_ISSUES, 1):
        print(f"\n{i}. Issue: {issue['title']}")
        
        component_labels = detect_component_labels(issue['title'], issue['body'])
        type_labels = detect_type_labels(issue['title'], issue['body'])
        priority = detect_priority(issue['title'], issue['body'])
        effort = detect_effort(issue['title'], issue['body'])
        
        print(f"   Components: {component_labels}")
        print(f"   Types: {type_labels}")
        print(f"   Priority: {priority}")
        print(f"   Effort: {effort}")
    
    # Test comment commands
    print("\n💬 Testing Comment Commands:")
    command_results = test_comment_commands()
    for result in command_results:
        print(f"   '{result['comment']}' → {result['detected_command']}")
    
    # Validate automation coverage
    print("\n📊 Automation Coverage Analysis:")
    total_issues = len(TEST_ISSUES)
    issues_with_components = sum(1 for issue in TEST_ISSUES 
                                if detect_component_labels(issue['title'], issue['body']))
    issues_with_types = sum(1 for issue in TEST_ISSUES 
                           if detect_type_labels(issue['title'], issue['body']))
    
    print(f"   Issues with component detection: {issues_with_components}/{total_issues} ({100*issues_with_components/total_issues:.1f}%)")
    print(f"   Issues with type detection: {issues_with_types}/{total_issues} ({100*issues_with_types/total_issues:.1f}%)")
    print(f"   All issues get priority: {total_issues}/{total_issues} (100.0%)")
    print(f"   All issues get effort: {total_issues}/{total_issues} (100.0%)")
    
    print("\n✅ Automation tests completed successfully!")
    print("\nNext steps:")
    print("1. Run python .github/setup-project-labels.py to create labels")
    print("2. Test with real issues to validate automation")
    print("3. Configure project board URL in workflows")

if __name__ == "__main__":
    run_automation_tests()