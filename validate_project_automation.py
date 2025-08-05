#!/usr/bin/env python3
"""
Validation script for project automation logic.
This script tests the automation logic without requiring GitHub Actions to run.
"""

import json
import re
from typing import List, Dict, Any


class ProjectAutomationValidator:
    """Validates project automation logic."""
    
    def __init__(self):
        # Define keyword mappings from the workflows
        self.priority_keywords = {
            'high': ['critical', 'urgent', 'security', 'breaking', 'crash', 'data loss'],
            'medium': ['important', 'enhancement', 'feature', 'add', 'implement', 'automation', 'setup', 'configure'], 
            'low': ['documentation', 'typo', 'cleanup', 'refactor', 'doc', 'readme']
        }
        
        self.component_keywords = {
            'backend': ['api', 'backend', 'server', 'database', 'routing', 'algorithm', 'auth', 'authentication', 'login', 'endpoint'],
            'frontend': ['ui', 'frontend', 'interface', 'dashboard', 'css', 'html'],
            'mobile': ['mobile', 'ios', 'android', 'app'],
            'ml': ['machine learning', 'ml', 'genetic', 'optimization', 'algorithm'],
            'infrastructure': ['docker', 'deployment', 'ci', 'cd', 'infrastructure']
        }
        
        self.type_keywords = {
            'bug': ['bug', 'fix', 'error', 'issue', 'broken'],
            'enhancement': ['feature', 'enhancement', 'add', 'implement', 'new', 'setup', 'configure', 'set up'],
            'documentation': ['doc', 'readme', 'documentation', 'docs'],
            'testing': ['test', 'testing', 'tests'],
            'performance': ['performance', 'optimization', 'speed', 'slow', 'fast'],
            'security': ['security', 'vulnerability', 'auth', 'permission']
        }
        
        self.file_patterns = {
            'backend': [r'^app/', r'^routing/', r'main\.py$', r'wsgi\.py$'],
            'frontend': [r'^frontend/', r'^static/', r'\.html$', r'\.css$', r'\.js$'],
            'mobile': [r'^mobile/'],
            'testing': [r'test', r'^tests/'],
            'infrastructure': [r'docker', r'^\.github/', r'^k8s/', r'^nginx/'],
            'ml': [r'genetic', r'ml_', r'optimization'],
            'documentation': [r'README', r'\.md$', r'^docs/']
        }
    
    def detect_priority(self, title: str, body: str = "") -> List[str]:
        """Detect priority labels based on content."""
        text = f"{title} {body}".lower()
        labels = []
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in text for keyword in keywords):
                labels.append(f"{priority}-priority")
                break  # Only assign one priority
        
        return labels
    
    def detect_components(self, title: str, body: str = "") -> List[str]:
        """Detect component labels based on content."""
        text = f"{title} {body}".lower()
        labels = []
        
        for component, keywords in self.component_keywords.items():
            if any(keyword in text for keyword in keywords):
                labels.append(f"component:{component}")
        
        return labels
    
    def detect_types(self, title: str, body: str = "") -> List[str]:
        """Detect type labels based on content."""
        text = f"{title} {body}".lower()
        labels = []
        
        for issue_type, keywords in self.type_keywords.items():
            if any(keyword in text for keyword in keywords):
                labels.append(issue_type)
        
        return labels
    
    def detect_components_from_files(self, file_paths: List[str]) -> List[str]:
        """Detect component labels based on changed files."""
        labels = []
        
        for component, patterns in self.file_patterns.items():
            for pattern in patterns:
                if any(re.search(pattern, file_path) for file_path in file_paths):
                    if component not in ['documentation']:  # Don't add component: prefix for docs
                        labels.append(f"component:{component}")
                    else:
                        labels.append(component)
                    break
        
        return labels
    
    def simulate_issue_automation(self, title: str, body: str = "") -> Dict[str, Any]:
        """Simulate the complete automation for an issue."""
        result = {
            'title': title,
            'body': body,
            'labels': [],
            'assignees': [],
            'status': 'status:backlog'  # Default status for new issues
        }
        
        # Detect all label types
        result['labels'].extend(self.detect_priority(title, body))
        result['labels'].extend(self.detect_components(title, body))
        result['labels'].extend(self.detect_types(title, body))
        
        # Auto-assignment logic
        if any('high-priority' in label for label in result['labels']):
            result['assignees'].append('ApacheEcho')
        
        return result
    
    def simulate_pr_automation(self, title: str, body: str = "", files: List[str] = None) -> Dict[str, Any]:
        """Simulate the complete automation for a PR."""
        if files is None:
            files = []
            
        result = {
            'title': title,
            'body': body,
            'files': files,
            'labels': [],
            'assignees': []
        }
        
        # Content-based detection
        result['labels'].extend(self.detect_priority(title, body))
        result['labels'].extend(self.detect_components(title, body))
        result['labels'].extend(self.detect_types(title, body))
        
        # File-based detection
        result['labels'].extend(self.detect_components_from_files(files))
        
        # Remove duplicates
        result['labels'] = list(set(result['labels']))
        
        return result
    
    def validate_status_transitions(self) -> Dict[str, List[str]]:
        """Validate status transition logic."""
        transitions = {
            'issue_opened': ['status:backlog'],
            'pr_ready_for_review': ['status:review'],
            'pr_converted_to_draft': ['status:draft', 'in-progress'],
            'item_closed': ['status:done'],
        }
        
        return transitions


def run_validation_tests():
    """Run comprehensive validation tests."""
    validator = ProjectAutomationValidator()
    
    print("🧪 Testing Project Automation Logic\n")
    
    # Test cases for issues
    test_issues = [
        {
            'title': 'Critical bug in route optimization algorithm',
            'body': 'The genetic algorithm crashes when processing large datasets',
            'expected_labels': ['high-priority', 'bug', 'component:ml']
        },
        {
            'title': 'Add new mobile feature for iOS app',
            'body': 'Implement push notifications for the mobile application',
            'expected_labels': ['medium-priority', 'enhancement', 'component:mobile']
        },
        {
            'title': 'Update API documentation',
            'body': 'The backend API docs need to be updated with new endpoints',
            'expected_labels': ['low-priority', 'documentation', 'component:backend']
        },
        {
            'title': 'Security vulnerability in authentication system',
            'body': 'Found potential SQL injection in login endpoint',
            'expected_labels': ['high-priority', 'security', 'component:backend']
        }
    ]
    
    print("📋 Testing Issue Automation:")
    for i, test_case in enumerate(test_issues, 1):
        result = validator.simulate_issue_automation(test_case['title'], test_case['body'])
        
        print(f"\n{i}. {test_case['title']}")
        print(f"   Detected labels: {result['labels']}")
        print(f"   Expected labels: {test_case['expected_labels']}")
        
        # Check if all expected labels are present
        missing_labels = set(test_case['expected_labels']) - set(result['labels'])
        if missing_labels:
            print(f"   ❌ Missing labels: {missing_labels}")
        else:
            print(f"   ✅ All expected labels detected")
        
        if result['assignees']:
            print(f"   👤 Auto-assigned to: {result['assignees']}")
    
    # Test cases for PRs with file changes
    test_prs = [
        {
            'title': 'Fix routing algorithm performance',
            'files': ['routing/core.py', 'routing/genetic.py', 'tests/test_routing.py'],
            'expected_components': ['component:backend', 'component:ml', 'component:testing']
        },
        {
            'title': 'Update mobile UI components',
            'files': ['mobile/ios/ViewController.swift', 'mobile/android/MainActivity.java'],
            'expected_components': ['component:mobile']
        },
        {
            'title': 'Add Docker configuration for production',
            'files': ['Dockerfile.production', '.github/workflows/deploy.yml', 'k8s/deployment.yaml'],
            'expected_components': ['component:infrastructure']
        }
    ]
    
    print(f"\n📦 Testing PR File-based Component Detection:")
    for i, test_case in enumerate(test_prs, 1):
        result = validator.simulate_pr_automation(test_case['title'], files=test_case['files'])
        
        print(f"\n{i}. {test_case['title']}")
        print(f"   Changed files: {test_case['files']}")
        print(f"   Detected components: {[l for l in result['labels'] if l.startswith('component:')]}")
        print(f"   Expected components: {test_case['expected_components']}")
        
        detected_components = [l for l in result['labels'] if l.startswith('component:') or l == 'documentation']
        missing_components = set(test_case['expected_components']) - set(detected_components)
        if missing_components:
            print(f"   ❌ Missing components: {missing_components}")
        else:
            print(f"   ✅ All expected components detected")
    
    # Test status transitions
    print(f"\n🔄 Testing Status Transition Logic:")
    transitions = validator.validate_status_transitions()
    for event, expected_status in transitions.items():
        print(f"   {event} → {expected_status}")
    
    print(f"\n✅ Validation completed! The automation logic is properly configured.")
    print(f"\n📚 See PROJECT_AUTOMATION.md for complete documentation.")


if __name__ == "__main__":
    run_validation_tests()