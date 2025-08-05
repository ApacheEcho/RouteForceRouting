#!/usr/bin/env python3
"""
GitHub Label Standardization Demo

This script demonstrates the label standardization system without requiring
actual GitHub API access. It shows how the labels would be processed and applied.
"""

import yaml
import json
from typing import Dict, List

def load_label_config():
    """Load and display the label configuration."""
    with open('.github/labels.yml', 'r') as f:
        config = yaml.safe_load(f)
    return config

def categorize_labels(labels: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize labels by their prefix."""
    categories = {
        'priority': [],
        'type': [],
        'status': [], 
        'component': [],
        'special': []
    }
    
    for label in labels:
        name = label['name']
        if ':' in name:
            category = name.split(':', 1)[0]
            if category in categories:
                categories[category].append(label)
            else:
                categories['special'].append(label)
        else:
            categories['special'].append(label)
    
    return categories

def demo_label_system():
    """Demonstrate the label standardization system."""
    print("🏷️  GitHub Label Standardization Demo")
    print("=" * 50)
    
    # Load configuration
    config = load_label_config()
    labels = config.get('labels', [])
    legacy_labels = config.get('remove', [])
    
    print(f"\n📊 Label Statistics:")
    print(f"   Total labels: {len(labels)}")
    print(f"   Legacy labels to remove: {len(legacy_labels)}")
    
    # Categorize labels
    categories = categorize_labels(labels)
    
    print(f"\n📋 Label Categories:")
    for category, category_labels in categories.items():
        if category_labels:
            print(f"   {category.title()}: {len(category_labels)} labels")
    
    print(f"\n🎨 Sample Labels by Category:")
    
    for category, category_labels in categories.items():
        if category_labels:
            print(f"\n   {category.title().upper()} LABELS:")
            for label in category_labels[:3]:  # Show first 3 of each category
                print(f"   • {label['name']} (#{label['color']}) - {label['description']}")
            if len(category_labels) > 3:
                print(f"   ... and {len(category_labels) - 3} more")
    
    print(f"\n🔄 Legacy Label Migration:")
    for old_label in legacy_labels:
        # Find replacement
        if old_label == "enhancement":
            replacement = "type:enhancement"
        elif old_label == "triage":
            replacement = "status:triage"
        elif old_label == "high-priority":
            replacement = "priority:high"
        elif old_label == "medium-priority":
            replacement = "priority:medium"
        else:
            replacement = "N/A"
        
        print(f"   {old_label} → {replacement}")
    
    print(f"\n💡 Example Issue Labeling:")
    examples = [
        {
            "title": "Fix critical security vulnerability in authentication",
            "labels": ["priority:critical", "type:security", "status:triage", "component:backend"]
        },
        {
            "title": "Add route optimization for mobile app",
            "labels": ["priority:medium", "type:feature", "status:in-progress", "component:mobile", "component:routing"]
        },
        {
            "title": "Update API documentation for v2.0",
            "labels": ["priority:low", "type:documentation", "status:review", "component:api"]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n   Example {i}: {example['title']}")
        print(f"   Labels: {', '.join(example['labels'])}")
    
    print(f"\n🚀 Automation Features:")
    print("   • Auto-assign labels based on issue templates")
    print("   • Detect priority from issue titles (critical/urgent)")
    print("   • Add blocked status when issues reference dependencies")
    print("   • Route to appropriate team members based on components")
    print("   • Integrate with GitHub project boards and workflows")
    
    print(f"\n✅ System Ready!")
    print("   The label standardization system is configured and ready to use.")
    print("   Run 'python scripts/standardize_labels.py' to apply labels to the repository.")

if __name__ == "__main__":
    demo_label_system()