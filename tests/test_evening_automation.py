"""
Test for evening automation functionality.
"""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
from scripts.evening_priorities import (
    analyze_git_status,
    analyze_test_results,
    scan_todo_items,
    generate_evening_priorities,
)


class TestEveningAutomation:
    """Test evening automation features."""

    def test_evening_priorities_structure(self):
        """Test that evening priorities generates the expected data structure."""
        priorities = generate_evening_priorities()
        
        # Check required fields
        assert "generated_at" in priorities
        assert "session_type" in priorities
        assert "git_status" in priorities
        assert "test_status" in priorities
        assert "todo_items" in priorities
        assert "file_changes" in priorities
        assert "recommendations" in priorities
        
        # Verify session type
        assert priorities["session_type"] == "evening_development"
        
        # Check git status structure
        git_status = priorities["git_status"]
        assert "branch" in git_status
        assert "uncommitted_changes" in git_status
        assert "unpushed_commits" in git_status
        
        # Check recommendations are present
        assert len(priorities["recommendations"]) > 0
        assert isinstance(priorities["recommendations"], list)

    def test_analyze_git_status(self):
        """Test git status analysis."""
        with patch('scripts.evening_priorities.run_git_command') as mock_git:
            mock_git.side_effect = [
                "main",  # branch
                "",      # no uncommitted changes
                "",      # no unpushed commits
                "0\t0"   # ahead/behind count
            ]
            
            status = analyze_git_status()
            
            assert status["branch"] == "main"
            assert status["uncommitted_changes"] is False
            assert status["unpushed_commits"] is False

    def test_analyze_test_results(self):
        """Test test results analysis."""
        results = analyze_test_results()
        
        # Should return a dict with expected keys
        assert "last_run" in results
        assert "passed" in results
        assert "failed" in results
        assert "skipped" in results
        assert "coverage" in results

    def test_scan_todo_items(self):
        """Test TODO item scanning."""
        # Create a temporary Python file with TODO items
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# TODO: This is a test todo item\n")
            f.write("def test_function():\n")
            f.write("    # FIXME: This needs fixing\n")
            f.write("    pass\n")
            temp_file = f.name
        
        try:
            # Mock Path.rglob to return our temp file
            with patch('pathlib.Path.rglob') as mock_rglob:
                mock_rglob.return_value = [temp_file]
                
                todos = scan_todo_items()
                
                # Should find the TODO items
                assert len(todos) >= 2
                assert any("TODO: This is a test todo item" in todo for todo in todos)
                assert any("FIXME: This needs fixing" in todo for todo in todos)
        finally:
            os.unlink(temp_file)

    def test_priorities_json_serializable(self):
        """Test that generated priorities can be serialized to JSON."""
        priorities = generate_evening_priorities()
        
        # Should be able to serialize to JSON without errors
        json_str = json.dumps(priorities)
        
        # Should be able to deserialize back
        restored = json.loads(json_str)
        
        assert restored["session_type"] == "evening_development"

    def test_recommendations_generation(self):
        """Test that recommendations are generated based on analysis."""
        with patch('scripts.evening_priorities.analyze_git_status') as mock_git:
            mock_git.return_value = {
                "branch": "feature-branch",
                "uncommitted_changes": True,
                "unpushed_commits": True,
                "ahead_behind": "1\t0"
            }
            
            priorities = generate_evening_priorities()
            recommendations = priorities["recommendations"]
            
            # Should include recommendations for uncommitted and unpushed changes
            assert any("commit pending changes" in rec.lower() for rec in recommendations)
            assert any("push local commits" in rec.lower() for rec in recommendations)

    @pytest.mark.integration
    def test_evening_automation_workflow_files_exist(self):
        """Test that evening automation workflow files exist."""
        # Check that the workflow file exists
        workflow_file = ".github/workflows/evening-automation.yml"
        assert os.path.exists(workflow_file), f"Workflow file {workflow_file} should exist"
        
        # Check that the script exists
        script_file = "scripts/evening_priorities.py"
        assert os.path.exists(script_file), f"Script file {script_file} should exist"
        
        # Check script is executable
        assert os.access(script_file, os.X_OK), f"Script {script_file} should be executable"