#!/usr/bin/env python3
"""
Test script for GitHub Label Standardization

This script validates the label configuration and tests the standardization logic
without making actual changes to the GitHub repository.
"""

import os
import sys
import yaml
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the scripts directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    from standardize_labels import LabelStandardizer
except ImportError as e:
    print(f"Error importing standardize_labels: {e}")
    print("Please ensure PyGithub and PyYAML are installed: pip install PyGithub PyYAML")
    sys.exit(1)

class TestLabelStandardization(unittest.TestCase):
    """Test cases for the label standardization system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_config = {
            'labels': [
                {
                    'name': 'priority:high',
                    'color': 'D93F0B',
                    'description': 'High priority issue'
                },
                {
                    'name': 'type:bug',
                    'color': 'D73A4A',
                    'description': 'Something is broken'
                }
            ],
            'remove': ['legacy-label']
        }
        
        # Create a temporary config file
        self.config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        yaml.dump(self.sample_config, self.config_file)
        self.config_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.config_file.name)
    
    def test_load_label_config(self):
        """Test loading label configuration from YAML file."""
        with patch('standardize_labels.Github'):
            standardizer = LabelStandardizer('test/repo', 'fake_token')
            config = standardizer.load_label_config(self.config_file.name)
            
            self.assertEqual(len(config['labels']), 2)
            self.assertEqual(config['labels'][0]['name'], 'priority:high')
            self.assertEqual(config['remove'], ['legacy-label'])
    
    def test_label_categories(self):
        """Test that all required label categories are present."""
        # Load the actual configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'labels.yml')
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        labels = config.get('labels', [])
        label_names = [label['name'] for label in labels]
        
        # Check for priority labels
        priority_labels = [name for name in label_names if name.startswith('priority:')]
        self.assertGreaterEqual(len(priority_labels), 4, "Should have at least 4 priority levels")
        
        # Check for type labels
        type_labels = [name for name in label_names if name.startswith('type:')]
        self.assertGreaterEqual(len(type_labels), 6, "Should have at least 6 issue types")
        
        # Check for status labels
        status_labels = [name for name in label_names if name.startswith('status:')]
        self.assertGreaterEqual(len(status_labels), 5, "Should have at least 5 status types")
        
        # Check for component labels
        component_labels = [name for name in label_names if name.startswith('component:')]
        self.assertGreaterEqual(len(component_labels), 6, "Should have at least 6 components")
    
    def test_color_format(self):
        """Test that all colors are valid hex codes."""
        config_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'labels.yml')
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        labels = config.get('labels', [])
        
        for label in labels:
            color = label.get('color', '')
            self.assertRegex(color, r'^[0-9A-Fa-f]{6}$', 
                           f"Color '{color}' for label '{label['name']}' is not a valid hex code")
    
    def test_required_fields(self):
        """Test that all labels have required fields."""
        config_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'labels.yml')
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        labels = config.get('labels', [])
        
        for label in labels:
            self.assertIn('name', label, "Label must have a name")
            self.assertIn('color', label, f"Label '{label.get('name')}' must have a color")
            self.assertIn('description', label, f"Label '{label.get('name')}' must have a description")
            
            # Validate name format
            name = label['name']
            if ':' in name:
                category, value = name.split(':', 1)
                self.assertIn(category, ['priority', 'type', 'status', 'component'], 
                            f"Unknown category '{category}' in label '{name}'")
    
    @patch('standardize_labels.Github')
    def test_standardizer_initialization(self, mock_github):
        """Test LabelStandardizer initialization."""
        mock_repo = Mock()
        mock_github.return_value.get_repo.return_value = mock_repo
        
        standardizer = LabelStandardizer('test/repo', 'fake_token')
        
        self.assertEqual(standardizer.repo, mock_repo)
        mock_github.assert_called_once_with('fake_token')
        mock_github.return_value.get_repo.assert_called_once_with('test/repo')

def run_validation_tests():
    """Run all validation tests."""
    print("🧪 Running GitHub Label Standardization Tests...\n")
    
    # Check if the configuration file exists
    config_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'labels.yml')
    if not os.path.exists(config_path):
        print(f"❌ Configuration file not found: {config_path}")
        return False
    
    # Run the test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLabelStandardization)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All label standardization tests passed!")
        return True
    else:
        print(f"\n❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False

def validate_yaml_syntax():
    """Validate YAML syntax of the configuration file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', '.github', 'labels.yml')
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        print("✅ YAML syntax is valid")
        
        # Basic structure validation
        if 'labels' not in config:
            print("❌ Configuration must have 'labels' section")
            return False
        
        if not isinstance(config['labels'], list):
            print("❌ 'labels' section must be a list")
            return False
        
        print(f"✅ Found {len(config['labels'])} labels in configuration")
        
        if 'remove' in config:
            print(f"✅ Found {len(config['remove'])} legacy labels to remove")
        
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        return False

def main():
    """Main function to run all validations."""
    print("🏷️  GitHub Label Standardization Validation\n")
    
    success = True
    
    # Validate YAML syntax
    print("1. Validating YAML configuration...")
    success &= validate_yaml_syntax()
    print()
    
    # Run unit tests
    print("2. Running unit tests...")
    success &= run_validation_tests()
    print()
    
    if success:
        print("🎉 All validations passed! The label standardization system is ready.")
        return 0
    else:
        print("💥 Some validations failed. Please fix the issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())