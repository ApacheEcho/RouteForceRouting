#!/usr/bin/env python3
"""
GitHub Labels Management Script
Manages comprehensive label system for RouteForce Routing project
"""

import os
import sys
import yaml
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("Warning: PyGithub not available. Install with: pip install PyGithub")


@dataclass
class Label:
    """Represents a GitHub label"""
    name: str
    color: str
    description: str
    aliases: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class LabelsManager:
    """Manages GitHub repository labels"""
    
    def __init__(self, repo_name: str = None, token: str = None):
        self.repo_name = repo_name or os.environ.get('GITHUB_REPOSITORY', 'ApacheEcho/RouteForceRouting')
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.github = None
        self.repo = None
        
        if GITHUB_AVAILABLE and self.token:
            try:
                self.github = Github(self.token)
                self.repo = self.github.get_repo(self.repo_name)
            except Exception as e:
                print(f"Warning: Could not connect to GitHub: {e}")
    
    def load_labels_config(self, config_path: str = '.github/labels.yml') -> Dict[str, List[Label]]:
        """Load labels configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            labels = {}
            for category, label_list in config.items():
                if category.startswith('#'):  # Skip comments
                    continue
                    
                labels[category] = []
                for label_data in label_list:
                    label = Label(
                        name=label_data['name'],
                        color=label_data['color'],
                        description=label_data['description'],
                        aliases=label_data.get('aliases', [])
                    )
                    labels[category].append(label)
            
            return labels
            
        except FileNotFoundError:
            print(f"Error: Configuration file {config_path} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            sys.exit(1)
    
    def get_existing_labels(self) -> Dict[str, any]:
        """Get existing labels from GitHub repository"""
        if not self.repo:
            print("Warning: Not connected to GitHub, cannot fetch existing labels")
            return {}
        
        existing = {}
        try:
            for label in self.repo.get_labels():
                existing[label.name] = {
                    'color': label.color,
                    'description': label.description or '',
                    'github_label': label
                }
        except Exception as e:
            print(f"Error fetching existing labels: {e}")
        
        return existing
    
    def sync_labels(self, dry_run: bool = False) -> Dict[str, List[str]]:
        """Synchronize labels with GitHub repository"""
        if not self.repo and not dry_run:
            print("Error: Not connected to GitHub. Use --dry-run to preview changes.")
            sys.exit(1)
        
        labels_config = self.load_labels_config()
        existing_labels = self.get_existing_labels() if not dry_run else {}
        
        results = {
            'created': [],
            'updated': [],
            'skipped': [],
            'errors': []
        }
        
        # Flatten all labels from all categories
        all_labels = []
        for category, labels in labels_config.items():
            all_labels.extend(labels)
        
        for label in all_labels:
            try:
                if label.name in existing_labels:
                    # Check if update is needed
                    existing = existing_labels[label.name]
                    if (existing['color'].upper() != label.color.upper() or 
                        existing['description'] != label.description):
                        
                        if dry_run:
                            print(f"Would update: {label.name}")
                            results['updated'].append(label.name)
                        else:
                            existing['github_label'].edit(
                                name=label.name,
                                color=label.color,
                                description=label.description
                            )
                            print(f"Updated: {label.name}")
                            results['updated'].append(label.name)
                    else:
                        results['skipped'].append(label.name)
                else:
                    # Create new label
                    if dry_run:
                        print(f"Would create: {label.name}")
                        results['created'].append(label.name)
                    else:
                        self.repo.create_label(
                            name=label.name,
                            color=label.color,
                            description=label.description
                        )
                        print(f"Created: {label.name}")
                        results['created'].append(label.name)
            
            except Exception as e:
                error_msg = f"Error processing {label.name}: {e}"
                print(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    def cleanup_old_labels(self, dry_run: bool = False) -> List[str]:
        """Remove deprecated labels that are no longer in the configuration"""
        if not self.repo and not dry_run:
            print("Error: Not connected to GitHub. Use --dry-run to preview changes.")
            return []
        
        labels_config = self.load_labels_config()
        existing_labels = self.get_existing_labels() if not dry_run else {}
        
        # Get all configured label names and aliases
        configured_names = set()
        for category, labels in labels_config.items():
            for label in labels:
                configured_names.add(label.name)
                configured_names.update(label.aliases)
        
        # Find labels to remove
        to_remove = []
        for existing_name in existing_labels.keys():
            if existing_name not in configured_names:
                to_remove.append(existing_name)
        
        # Remove deprecated labels
        removed = []
        for label_name in to_remove:
            try:
                if dry_run:
                    print(f"Would remove: {label_name}")
                    removed.append(label_name)
                else:
                    existing_labels[label_name]['github_label'].delete()
                    print(f"Removed: {label_name}")
                    removed.append(label_name)
            except Exception as e:
                print(f"Error removing {label_name}: {e}")
        
        return removed
    
    def export_labels(self, format_type: str = 'json') -> str:
        """Export current labels configuration"""
        labels_config = self.load_labels_config()
        
        if format_type == 'json':
            # Convert to JSON-serializable format
            export_data = {}
            for category, labels in labels_config.items():
                export_data[category] = []
                for label in labels:
                    export_data[category].append({
                        'name': label.name,
                        'color': label.color,
                        'description': label.description,
                        'aliases': label.aliases
                    })
            return json.dumps(export_data, indent=2)
        
        elif format_type == 'markdown':
            # Generate markdown documentation
            md = "# GitHub Labels Documentation\n\n"
            md += "This document describes the standardized label system for the RouteForce Routing project.\n\n"
            
            for category, labels in labels_config.items():
                md += f"## {category.title()} Labels\n\n"
                for label in labels:
                    color_hex = f"#{label.color}"
                    md += f"### `{label.name}`\n"
                    md += f"- **Color**: {color_hex} ![{color_hex}](https://via.placeholder.com/20x20/{label.color}/{label.color})\n"
                    md += f"- **Description**: {label.description}\n"
                    if label.aliases:
                        md += f"- **Aliases**: {', '.join(label.aliases)}\n"
                    md += "\n"
                md += "\n"
            
            return md
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def validate_config(self) -> bool:
        """Validate the labels configuration"""
        try:
            labels_config = self.load_labels_config()
            
            # Check for duplicate names
            all_names = []
            for category, labels in labels_config.items():
                for label in labels:
                    all_names.append(label.name)
            
            if len(all_names) != len(set(all_names)):
                print("Error: Duplicate label names found")
                return False
            
            # Check color format
            for category, labels in labels_config.items():
                for label in labels:
                    if not label.color or len(label.color) != 6:
                        print(f"Error: Invalid color format for {label.name}: {label.color}")
                        return False
                    
                    try:
                        int(label.color, 16)
                    except ValueError:
                        print(f"Error: Invalid hex color for {label.name}: {label.color}")
                        return False
            
            print("Configuration validation passed")
            return True
            
        except Exception as e:
            print(f"Validation error: {e}")
            return False


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Labels Management')
    parser.add_argument('--repo', help='GitHub repository (owner/repo)')
    parser.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Synchronize labels with GitHub')
    sync_parser.add_argument('--cleanup', action='store_true', help='Also remove deprecated labels')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export labels configuration')
    export_parser.add_argument('--format', choices=['json', 'markdown'], default='json',
                              help='Export format')
    export_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    manager = LabelsManager(args.repo, args.token)
    
    if args.command == 'sync':
        print("Synchronizing labels...")
        results = manager.sync_labels(dry_run=args.dry_run)
        
        print(f"\nResults:")
        print(f"- Created: {len(results['created'])}")
        print(f"- Updated: {len(results['updated'])}")
        print(f"- Skipped: {len(results['skipped'])}")
        print(f"- Errors: {len(results['errors'])}")
        
        if args.cleanup:
            print("\nCleaning up deprecated labels...")
            removed = manager.cleanup_old_labels(dry_run=args.dry_run)
            print(f"- Removed: {len(removed)}")
    
    elif args.command == 'export':
        output = manager.export_labels(args.format)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Exported to {args.output}")
        else:
            print(output)
    
    elif args.command == 'validate':
        if manager.validate_config():
            print("✅ Configuration is valid")
            sys.exit(0)
        else:
            print("❌ Configuration has errors")
            sys.exit(1)


if __name__ == '__main__':
    main()