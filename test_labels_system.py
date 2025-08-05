#!/usr/bin/env python3
"""
Test script for GitHub Labels system
Validates that the labels system is properly configured and functional
"""

import os
import sys
import yaml
import json

def test_labels_config():
    """Test that labels configuration is valid"""
    try:
        with open('.github/labels.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check required categories exist
        required_categories = ['priority', 'type', 'status', 'component', 'special']
        for category in required_categories:
            if category not in config:
                print(f"❌ Missing category: {category}")
                return False
        
        # Check that each category has labels
        total_labels = 0
        for category, labels in config.items():
            if not labels:
                print(f"❌ Empty category: {category}")
                return False
            
            for label in labels:
                if not all(key in label for key in ['name', 'color', 'description']):
                    print(f"❌ Invalid label format in {category}: {label}")
                    return False
                total_labels += 1
        
        print(f"✅ Labels config valid - {total_labels} labels across {len(config)} categories")
        return True
        
    except Exception as e:
        print(f"❌ Error testing labels config: {e}")
        return False

def test_issue_templates():
    """Test that issue templates use standardized labels"""
    templates_dir = '.github/ISSUE_TEMPLATE'
    if not os.path.exists(templates_dir):
        print(f"❌ Issue templates directory not found: {templates_dir}")
        return False
    
    template_files = [f for f in os.listdir(templates_dir) if f.endswith('.yml')]
    if not template_files:
        print(f"❌ No YAML templates found in {templates_dir}")
        return False
    
    for template_file in template_files:
        try:
            with open(os.path.join(templates_dir, template_file), 'r') as f:
                template = yaml.safe_load(f)
            
            if 'labels' not in template:
                print(f"⚠️  No labels defined in {template_file}")
                continue
            
            # Check that labels follow new format
            labels = template['labels']
            standardized = any('/' in label for label in labels)
            if not standardized:
                print(f"⚠️  {template_file} may not use standardized labels: {labels}")
            else:
                print(f"✅ {template_file} uses standardized labels: {labels}")
                
        except Exception as e:
            print(f"❌ Error reading template {template_file}: {e}")
            return False
    
    return True

def test_management_script():
    """Test that the management script works"""
    try:
        # Test import
        sys.path.insert(0, 'scripts')
        from manage_labels import LabelsManager
        
        # Test validation
        manager = LabelsManager()
        if manager.validate_config():
            print("✅ Management script validation passed")
            return True
        else:
            print("❌ Management script validation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing management script: {e}")
        return False

def test_documentation():
    """Test that documentation files exist and are readable"""
    docs = ['.github/LABELS.md', '.github/LABELS_README.md']
    
    for doc in docs:
        if not os.path.exists(doc):
            print(f"❌ Documentation not found: {doc}")
            return False
        
        try:
            with open(doc, 'r') as f:
                content = f.read()
            if len(content) < 100:
                print(f"⚠️  Documentation seems too short: {doc}")
            else:
                print(f"✅ Documentation exists and has content: {doc}")
        except Exception as e:
            print(f"❌ Error reading documentation {doc}: {e}")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing GitHub Labels System\n")
    
    tests = [
        ("Labels Configuration", test_labels_config),
        ("Issue Templates", test_issue_templates), 
        ("Management Script", test_management_script),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"💥 {test_name} failed")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Labels system is ready.")
        return 0
    else:
        print("🚨 Some tests failed. Please review the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())