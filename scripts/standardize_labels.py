#!/usr/bin/env python3
"""
GitHub Label Standardization Script

This script applies the comprehensive label system defined in .github/labels.yml
to standardize GitHub labels across the RouteForceRouting repository.

Usage:
    python scripts/standardize_labels.py

Requirements:
    - PyGithub library: pip install PyGithub
    - GitHub token with repo access (set as GITHUB_TOKEN env var)
"""

import os
import sys
import yaml
import logging
import argparse
from typing import Dict, List, Optional
from github import Github
from github.GithubException import GithubException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LabelStandardizer:
    def __init__(self, repo_name: str, github_token: str):
        """Initialize the label standardizer."""
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)
        self.existing_labels = {}
        
    def load_label_config(self, config_path: str) -> Dict:
        """Load label configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            sys.exit(1)
    
    def get_existing_labels(self) -> Dict[str, object]:
        """Get all existing labels in the repository."""
        logger.info("Fetching existing labels...")
        try:
            labels = self.repo.get_labels()
            self.existing_labels = {label.name: label for label in labels}
            logger.info(f"Found {len(self.existing_labels)} existing labels")
            return self.existing_labels
        except GithubException as e:
            logger.error(f"Error fetching existing labels: {e}")
            sys.exit(1)
    
    def create_or_update_label(self, label_config: Dict) -> bool:
        """Create a new label or update an existing one."""
        name = label_config['name']
        color = label_config['color']
        description = label_config.get('description', '')
        
        try:
            if name in self.existing_labels:
                # Update existing label
                label = self.existing_labels[name]
                if label.color != color or label.description != description:
                    label.edit(name, color, description)
                    logger.info(f"Updated label: {name}")
                    return True
                else:
                    logger.debug(f"Label unchanged: {name}")
                    return False
            else:
                # Create new label
                self.repo.create_label(name, color, description)
                logger.info(f"Created label: {name}")
                return True
        except GithubException as e:
            logger.error(f"Error creating/updating label '{name}': {e}")
            return False
    
    def remove_legacy_labels(self, labels_to_remove: List[str]) -> int:
        """Remove legacy labels that are no longer needed."""
        removed_count = 0
        
        for label_name in labels_to_remove:
            if label_name in self.existing_labels:
                try:
                    self.existing_labels[label_name].delete()
                    logger.info(f"Removed legacy label: {label_name}")
                    removed_count += 1
                except GithubException as e:
                    logger.error(f"Error removing label '{label_name}': {e}")
            else:
                logger.debug(f"Legacy label not found: {label_name}")
        
        return removed_count
    
    def standardize_labels(self, config_path: str = '.github/labels.yml') -> Dict[str, int]:
        """Apply the comprehensive label standardization."""
        logger.info("Starting label standardization...")
        
        # Load configuration
        config = self.load_label_config(config_path)
        labels_config = config.get('labels', [])
        legacy_labels = config.get('remove', [])
        
        # Get existing labels
        self.get_existing_labels()
        
        # Track statistics
        stats = {
            'created': 0,
            'updated': 0,
            'removed': 0,
            'unchanged': 0
        }
        
        # Process each label in configuration
        for label_config in labels_config:
            if isinstance(label_config, dict) and 'name' in label_config:
                if self.create_or_update_label(label_config):
                    if label_config['name'] in self.existing_labels:
                        stats['updated'] += 1
                    else:
                        stats['created'] += 1
                else:
                    stats['unchanged'] += 1
        
        # Remove legacy labels
        if legacy_labels:
            stats['removed'] = self.remove_legacy_labels(legacy_labels)
        
        logger.info("Label standardization completed!")
        logger.info(f"Statistics: {stats}")
        
        return stats
    
    def validate_repository_labels(self) -> bool:
        """Validate that all required labels exist with correct configuration."""
        logger.info("Validating repository labels...")
        
        config = self.load_label_config('.github/labels.yml')
        labels_config = config.get('labels', [])
        
        self.get_existing_labels()
        
        all_valid = True
        
        for label_config in labels_config:
            if isinstance(label_config, dict) and 'name' in label_config:
                name = label_config['name']
                if name not in self.existing_labels:
                    logger.error(f"Required label missing: {name}")
                    all_valid = False
                else:
                    label = self.existing_labels[name]
                    if label.color != label_config['color']:
                        logger.warning(f"Label color mismatch for '{name}': expected {label_config['color']}, got {label.color}")
                        all_valid = False
        
        if all_valid:
            logger.info("✅ All repository labels are properly configured!")
        else:
            logger.error("❌ Repository labels need standardization")
        
        return all_valid

def main():
    """Main function to run label standardization."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Standardize GitHub repository labels')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate labels without making changes')
    args = parser.parse_args()
    
    # Check for GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    # Get repository name from environment or use default
    repo_name = os.getenv('GITHUB_REPOSITORY', 'ApacheEcho/RouteForceRouting')
    
    try:
        # Initialize standardizer
        standardizer = LabelStandardizer(repo_name, github_token)
        
        if args.validate_only:
            # Only validate existing labels
            if standardizer.validate_repository_labels():
                logger.info("🎉 Label validation successful!")
                return 0
            else:
                logger.error("❌ Label validation failed")
                return 1
        else:
            # Run standardization
            stats = standardizer.standardize_labels()
            
            # Validate results
            if standardizer.validate_repository_labels():
                logger.info("🎉 Label standardization successful!")
                return 0
            else:
                logger.error("⚠️ Label standardization completed but validation failed")
                return 1
            
    except Exception as e:
        logger.error(f"Fatal error during label standardization: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())