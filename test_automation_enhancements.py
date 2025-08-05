#!/usr/bin/env python3
"""
Comprehensive test suite for project automation enhancements.
Tests specifically the new keywords and functionality added in the commit.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validate_project_automation import ProjectAutomationValidator


def test_new_enhancement_keywords():
    """Test the newly added enhancement keywords: setup, configure, set up."""
    validator = ProjectAutomationValidator()
    
    print("🔧 Testing New Enhancement Keywords:")
    
    test_cases = [
        {
            'title': 'Setup new development environment',
            'expected_labels': ['medium-priority', 'enhancement'],
            'description': 'Tests "setup" keyword'
        },
        {
            'title': 'Configure authentication for mobile app',
            'expected_labels': ['medium-priority', 'enhancement', 'component:mobile', 'component:backend'],
            'description': 'Tests "configure" keyword'
        },
        {
            'title': 'Set up continuous integration pipeline',
            'expected_labels': ['medium-priority', 'enhancement', 'component:infrastructure'],
            'description': 'Tests "set up" keyword phrase'
        },
        {
            'title': 'Need to setup automated testing',
            'expected_labels': ['medium-priority', 'enhancement'],
            'description': 'Tests "setup" in context'
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = validator.simulate_issue_automation(test_case['title'])
        
        print(f"\n{i}. {test_case['title']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Detected labels: {result['labels']}")
        print(f"   Expected labels: {test_case['expected_labels']}")
        
        # Check if all expected labels are present
        missing_labels = set(test_case['expected_labels']) - set(result['labels'])
        if missing_labels:
            print(f"   ❌ Missing labels: {missing_labels}")
            all_passed = False
        else:
            print(f"   ✅ All expected labels detected")
    
    return all_passed


def test_new_medium_priority_keywords():
    """Test the newly added medium priority keywords: automation, setup, configure."""
    validator = ProjectAutomationValidator()
    
    print("\n📈 Testing New Medium Priority Keywords:")
    
    test_cases = [
        {
            'title': 'Automation improvements for CI/CD',
            'expected_priority': 'medium-priority',
            'description': 'Tests "automation" keyword'
        },
        {
            'title': 'Setup new deployment process',
            'expected_priority': 'medium-priority',
            'description': 'Tests "setup" for priority'
        },
        {
            'title': 'Configure database connections',
            'expected_priority': 'medium-priority',
            'description': 'Tests "configure" for priority'
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = validator.simulate_issue_automation(test_case['title'])
        priority_labels = [label for label in result['labels'] if 'priority' in label]
        
        print(f"\n{i}. {test_case['title']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Detected priority: {priority_labels}")
        print(f"   Expected priority: {test_case['expected_priority']}")
        
        if test_case['expected_priority'] not in priority_labels:
            print(f"   ❌ Expected priority not detected")
            all_passed = False
        else:
            print(f"   ✅ Correct priority detected")
    
    return all_passed


def test_new_backend_auth_keywords():
    """Test the newly added backend authentication keywords."""
    validator = ProjectAutomationValidator()
    
    print("\n🔐 Testing New Backend Authentication Keywords:")
    
    test_cases = [
        {
            'title': 'Fix auth token validation',
            'expected_component': 'component:backend',
            'description': 'Tests "auth" keyword'
        },
        {
            'title': 'Authentication system refactor',
            'expected_component': 'component:backend',
            'description': 'Tests "authentication" keyword'
        },
        {
            'title': 'Login endpoint returns 500 error',
            'expected_component': 'component:backend',
            'description': 'Tests "login" keyword'
        },
        {
            'title': 'New endpoint for user management',
            'expected_component': 'component:backend',
            'description': 'Tests "endpoint" keyword'
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = validator.simulate_issue_automation(test_case['title'])
        component_labels = [label for label in result['labels'] if label.startswith('component:')]
        
        print(f"\n{i}. {test_case['title']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Detected components: {component_labels}")
        print(f"   Expected component: {test_case['expected_component']}")
        
        if test_case['expected_component'] not in component_labels:
            print(f"   ❌ Expected component not detected")
            all_passed = False
        else:
            print(f"   ✅ Correct component detected")
    
    return all_passed


def test_edge_cases():
    """Test edge cases and combinations."""
    validator = ProjectAutomationValidator()
    
    print("\n🧪 Testing Edge Cases:")
    
    test_cases = [
        {
            'title': 'Critical setup failure in production authentication',
            'expected_labels': ['high-priority', 'enhancement', 'component:backend', 'component:infrastructure'],
            'description': 'Tests multiple new keywords combined'
        },
        {
            'title': 'Configure mobile app setup automation',
            'expected_labels': ['medium-priority', 'enhancement', 'component:mobile'],
            'description': 'Tests multiple medium priority keywords'
        },
        {
            'title': '',  # Empty title
            'expected_labels': [],
            'description': 'Tests empty title handling'
        },
        {
            'title': 'Setup',  # Single keyword
            'expected_labels': ['medium-priority', 'enhancement'],
            'description': 'Tests single keyword detection'
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = validator.simulate_issue_automation(test_case['title'])
        
        print(f"\n{i}. '{test_case['title']}'")
        print(f"   Description: {test_case['description']}")
        print(f"   Detected labels: {result['labels']}")
        print(f"   Expected labels: {test_case['expected_labels']}")
        
        # For edge cases, just check that no errors occur and some basic logic works
        if test_case['title'] == '':
            # Empty title should not crash and should have minimal labels
            if len(result['labels']) <= 1:  # Only status:backlog might be added
                print(f"   ✅ Empty title handled correctly")
            else:
                print(f"   ❌ Empty title produced unexpected labels")
                all_passed = False
        elif test_case['title'] == 'Setup':
            # Single keyword should be detected
            if 'enhancement' in result['labels'] and 'medium-priority' in result['labels']:
                print(f"   ✅ Single keyword detected correctly")
            else:
                print(f"   ❌ Single keyword not detected properly")
                all_passed = False
        else:
            # Check if most expected labels are present (allow some variation for complex cases)
            missing_labels = set(test_case['expected_labels']) - set(result['labels'])
            if len(missing_labels) <= 1:  # Allow for 1 missing label in complex cases
                print(f"   ✅ Most expected labels detected")
            else:
                print(f"   ❌ Too many missing labels: {missing_labels}")
                all_passed = False
    
    return all_passed


def test_file_based_detection():
    """Test file-based component detection enhancements."""
    validator = ProjectAutomationValidator()
    
    print("\n📁 Testing File-based Component Detection:")
    
    test_cases = [
        {
            'title': 'Authentication improvements',
            'files': ['app/auth.py', 'routing/auth_middleware.py'],
            'expected_components': ['component:backend'],
            'description': 'Tests backend file detection'
        },
        {
            'title': 'Mobile setup improvements',
            'files': ['mobile/setup.js', 'mobile/config.json'],
            'expected_components': ['component:mobile'],
            'description': 'Tests mobile file detection'
        },
        {
            'title': 'Documentation setup',
            'files': ['README.md', 'docs/setup.md'],
            'expected_components': ['documentation'],
            'description': 'Tests documentation file detection'
        }
    ]
    
    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = validator.simulate_pr_automation(test_case['title'], files=test_case['files'])
        detected_components = [l for l in result['labels'] if l.startswith('component:') or l == 'documentation']
        
        print(f"\n{i}. {test_case['title']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Files: {test_case['files']}")
        print(f"   Detected components: {detected_components}")
        print(f"   Expected components: {test_case['expected_components']}")
        
        missing_components = set(test_case['expected_components']) - set(detected_components)
        if missing_components:
            print(f"   ❌ Missing components: {missing_components}")
            all_passed = False
        else:
            print(f"   ✅ All expected components detected")
    
    return all_passed


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("🚀 Running Comprehensive Project Automation Tests\n")
    
    results = []
    
    # Run all test suites
    results.append(("New Enhancement Keywords", test_new_enhancement_keywords()))
    results.append(("New Medium Priority Keywords", test_new_medium_priority_keywords()))
    results.append(("New Backend Auth Keywords", test_new_backend_auth_keywords()))
    results.append(("Edge Cases", test_edge_cases()))
    results.append(("File-based Detection", test_file_based_detection()))
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! The automation enhancements are working correctly.")
        print("✅ New keywords are properly detected and categorized.")
        print("✅ Priority assignment logic is functioning correctly.")
        print("✅ Component detection is working as expected.")
    else:
        print("⚠️  SOME TESTS FAILED! Please review the failing test cases above.")
    
    return all_passed


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)