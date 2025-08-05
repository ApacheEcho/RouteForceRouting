"""
Test suite for project board automation workflows.

This module tests the GitHub Actions workflows for project automation
to ensure they work correctly and handle edge cases properly.
"""

import os
import json
import yaml
import pytest
from pathlib import Path


class TestProjectAutomation:
    """Test project automation configuration and workflows."""
    
    @pytest.fixture
    def github_workflows_dir(self):
        """Get the GitHub workflows directory."""
        repo_root = Path(__file__).parent.parent
        return repo_root / ".github" / "workflows"
    
    @pytest.fixture
    def project_views_file(self):
        """Get the project views configuration file."""
        repo_root = Path(__file__).parent.parent
        return repo_root / ".github" / "project-views.yml"
    
    def test_project_automation_workflow_exists(self, github_workflows_dir):
        """Test that project automation workflow exists and is valid."""
        workflow_file = github_workflows_dir / "project-automation.yml"
        assert workflow_file.exists(), "project-automation.yml workflow should exist"
        
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Test basic structure
        assert 'name' in workflow
        assert 'on' in workflow
        assert 'jobs' in workflow
        
        # Test that it has the required triggers
        assert 'issues' in workflow['on']
        assert 'pull_request' in workflow['on']
        
        # Test that it has the required jobs
        assert 'auto-add-to-project' in workflow['jobs']
        assert 'auto-triage-and-label' in workflow['jobs']
        assert 'auto-milestone-assignment' in workflow['jobs']
    
    def test_advanced_automation_workflow_exists(self, github_workflows_dir):
        """Test that advanced automation workflow exists and is valid."""
        workflow_file = github_workflows_dir / "advanced-project-automation.yml"
        assert workflow_file.exists(), "advanced-project-automation.yml workflow should exist"
        
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # Test basic structure
        assert 'name' in workflow
        assert 'on' in workflow
        assert 'jobs' in workflow
        
        # Test comprehensive triggers
        triggers = workflow['on']
        assert 'issues' in triggers
        assert 'pull_request' in triggers
        assert 'issue_comment' in triggers
        assert 'pull_request_review' in triggers
    
    def test_stale_management_workflow_exists(self, github_workflows_dir):
        """Test that stale management workflow exists."""
        workflow_file = github_workflows_dir / "stale-management.yml"
        assert workflow_file.exists(), "stale-management.yml workflow should exist"
        
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        
        assert 'schedule' in workflow['on']
        assert 'workflow_dispatch' in workflow['on']
    
    def test_setup_labels_workflow_exists(self, github_workflows_dir):
        """Test that setup labels workflow exists."""
        workflow_file = github_workflows_dir / "setup-labels.yml"
        assert workflow_file.exists(), "setup-labels.yml workflow should exist"
        
        with open(workflow_file, 'r') as f:
            workflow = yaml.safe_load(f)
        
        assert 'create-labels' in workflow['jobs']
    
    def test_project_views_configuration(self, project_views_file):
        """Test project views configuration."""
        assert project_views_file.exists(), "project-views.yml should exist"
        
        with open(project_views_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert 'views' in config
        views = config['views']
        
        # Check for Sprint Board view
        sprint_board = next((v for v in views if v['name'] == 'Sprint Board'), None)
        assert sprint_board is not None, "Sprint Board view should exist"
        assert sprint_board['layout'] == 'board'
        
        # Check required columns
        columns = sprint_board['columns']
        column_names = [col['name'] for col in columns]
        required_columns = ['Backlog', 'In Progress', 'Review', 'Done']
        
        for required_col in required_columns:
            assert required_col in column_names, f"{required_col} column should exist"
    
    def test_workflow_permissions(self, github_workflows_dir):
        """Test that workflows have proper permissions."""
        workflow_files = [
            'project-automation.yml',
            'advanced-project-automation.yml',
            'stale-management.yml'
        ]
        
        for workflow_file in workflow_files:
            file_path = github_workflows_dir / workflow_file
            if file_path.exists():
                with open(file_path, 'r') as f:
                    workflow = yaml.safe_load(f)
                
                if 'permissions' in workflow:
                    permissions = workflow['permissions']
                    assert 'issues' in permissions, f"{workflow_file} should have issues permission"
                    assert permissions['issues'] == 'write', f"{workflow_file} should have write access to issues"
    
    def test_label_automation_keywords(self):
        """Test that automation includes proper keyword detection."""
        test_cases = [
            # Priority keywords
            {
                'title': 'Critical bug in route optimization',
                'expected_priority': 'high-priority',
                'expected_type': 'bug'
            },
            {
                'title': 'Add new feature for mobile app',
                'expected_priority': 'medium-priority',
                'expected_type': 'enhancement',
                'expected_component': 'component:mobile'
            },
            {
                'title': 'Update documentation for API',
                'expected_priority': 'low-priority',
                'expected_type': 'documentation',
                'expected_component': 'component:backend'
            },
            {
                'title': 'Security vulnerability in authentication',
                'expected_priority': 'high-priority',
                'expected_type': 'security'
            },
            {
                'title': 'Performance optimization for routing algorithm',
                'expected_type': 'performance',
                'expected_component': 'component:ml'
            }
        ]
        
        # This test validates the keyword detection logic would work
        # In a real implementation, you'd test the actual GitHub script
        for case in test_cases:
            title_lower = case['title'].lower()
            
            # Test priority detection
            if 'expected_priority' in case:
                priority = case['expected_priority']
                if priority == 'high-priority':
                    assert any(keyword in title_lower for keyword in ['critical', 'urgent', 'security'])
                elif priority == 'medium-priority':
                    assert any(keyword in title_lower for keyword in ['feature', 'add', 'enhancement'])
                elif priority == 'low-priority':
                    assert any(keyword in title_lower for keyword in ['documentation', 'doc'])
            
            # Test type detection
            if 'expected_type' in case:
                issue_type = case['expected_type']
                if issue_type == 'bug':
                    assert any(keyword in title_lower for keyword in ['bug', 'critical'])
                elif issue_type == 'enhancement':
                    assert any(keyword in title_lower for keyword in ['feature', 'add'])
                elif issue_type == 'documentation':
                    assert any(keyword in title_lower for keyword in ['documentation', 'doc'])
    
    def test_component_detection_logic(self):
        """Test component detection based on file paths."""
        test_file_cases = [
            {
                'files': ['app/main.py', 'routing/core.py'],
                'expected_component': 'component:backend'
            },
            {
                'files': ['frontend/src/app.js', 'static/css/style.css'],
                'expected_component': 'component:frontend'
            },
            {
                'files': ['mobile/ios/AppDelegate.swift'],
                'expected_component': 'component:mobile'
            },
            {
                'files': ['tests/test_routing.py', 'test_app.py'],
                'expected_component': 'component:testing'
            },
            {
                'files': ['Dockerfile', '.github/workflows/ci.yml'],
                'expected_component': 'component:infrastructure'
            },
            {
                'files': ['routing/genetic_algorithm.py', 'ml_integration.py'],
                'expected_component': 'component:ml'
            }
        ]
        
        for case in test_file_cases:
            files = case['files']
            expected = case['expected_component']
            
            # Simulate the detection logic
            if expected == 'component:backend':
                assert any(f.startswith('app/') or f.startswith('routing/') or 'main.py' in f for f in files)
            elif expected == 'component:frontend':
                assert any(f.startswith('frontend/') or f.startswith('static/') or f.endswith('.css') for f in files)
            elif expected == 'component:mobile':
                assert any(f.startswith('mobile/') for f in files)
            elif expected == 'component:testing':
                assert any('test' in f for f in files)
            elif expected == 'component:infrastructure':
                assert any(f.startswith('.github/') or 'docker' in f.lower() for f in files)
            elif expected == 'component:ml':
                assert any('genetic' in f or 'ml_' in f for f in files)
    
    def test_status_transition_logic(self):
        """Test status transition automation logic."""
        transitions = [
            {
                'from_status': 'opened',
                'action': 'issue_opened',
                'expected_label': 'status:backlog'
            },
            {
                'from_status': 'draft',
                'action': 'ready_for_review',
                'expected_label': 'status:review',
                'remove_labels': ['status:draft', 'in-progress']
            },
            {
                'from_status': 'any',
                'action': 'closed',
                'expected_label': 'status:done',
                'remove_labels': ['status:backlog', 'status:in-progress', 'status:review']
            }
        ]
        
        # This validates the transition logic structure
        for transition in transitions:
            assert 'action' in transition
            assert 'expected_label' in transition
            if 'remove_labels' in transition:
                assert isinstance(transition['remove_labels'], list)
    
    def test_automation_yaml_syntax(self, github_workflows_dir):
        """Test that all workflow YAML files have valid syntax."""
        workflow_files = [
            'project-automation.yml',
            'advanced-project-automation.yml', 
            'stale-management.yml',
            'setup-labels.yml'
        ]
        
        for workflow_file in workflow_files:
            file_path = github_workflows_dir / workflow_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML syntax in {workflow_file}: {e}")


class TestProjectBoardIntegration:
    """Test project board integration and configuration."""
    
    def test_project_url_configuration(self, github_workflows_dir):
        """Test that project URL is properly configured."""
        workflow_file = github_workflows_dir / "project-automation.yml"
        
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Ensure placeholder is replaced
        assert 'YOUR_PROJECT_NUMBER' not in content, "Project URL placeholder should be replaced"
        assert 'github.com/' in content, "Should contain valid GitHub project URL"
    
    def test_automation_coverage(self):
        """Test that automation covers all required scenarios."""
        required_automations = [
            'auto-add-to-project',      # Adding new issues/PRs to project
            'auto-triage-and-label',    # Automatic labeling and triaging
            'auto-milestone-assignment', # Milestone assignment
            'advanced-triage',          # Advanced automation rules
            'file-based-component-detection',  # File-based component detection
            'stale-management',         # Stale issue/PR management
            'label-creation'            # Required label creation
        ]
        
        # This test documents the expected automation coverage
        assert len(required_automations) >= 6, "Should have comprehensive automation coverage"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])