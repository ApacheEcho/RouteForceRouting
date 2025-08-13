#!/usr/bin/env python3
"""
Tests for auto-commit service functionality
"""

import unittest
import tempfile
import os
import shutil
import subprocess
import threading
import time
from unittest.mock import patch, MagicMock

try:
    from app.services.auto_commit_service import AutoCommitService
except ImportError:
    import pytest
    pytest.skip("Main app modules not available; skipping test.", allow_module_level=True)


class TestAutoCommitService(unittest.TestCase):
    """Test the auto-commit service functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Initialize a git repository in the test directory
        os.chdir(self.test_dir)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        
        # Create initial commit
        with open("README.md", "w") as f:
            f.write("# Test Repository\n")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        self.service = AutoCommitService(repo_path=self.test_dir, interval_minutes=1)
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'service') and self.service.is_running:
            self.service.stop()
        
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        self.assertEqual(self.service.repo_path, self.test_dir)
        self.assertEqual(self.service.interval_seconds, 60)
        self.assertEqual(self.service.wip_branch, "auto-wip")
        self.assertFalse(self.service.is_running)
    
    def test_has_git_changes_no_changes(self):
        """Test detecting no changes"""
        self.assertFalse(self.service._has_git_changes())
    
    def test_has_git_changes_with_changes(self):
        """Test detecting changes"""
        # Create a new file
        with open("test_file.txt", "w") as f:
            f.write("Test content")
        
        self.assertTrue(self.service._has_git_changes())
    
    def test_get_current_branch(self):
        """Test getting current branch name"""
        branch = self.service._get_current_branch()
        # Should be 'main' or 'master' depending on git version
        self.assertIn(branch, ['main', 'master'])
    
    def test_generate_smart_commit_message_no_changes(self):
        """Test commit message generation with no changes"""
        message = self.service._generate_smart_commit_message()
        self.assertIn("Auto-save", message)
        self.assertIn("Backup changes", message)
    
    def test_generate_smart_commit_message_single_file(self):
        """Test commit message generation with single file change"""
        with open("new_file.py", "w") as f:
            f.write("print('hello')")
        
        message = self.service._generate_smart_commit_message()
        self.assertIn("Auto-save", message)
        self.assertIn("new_file.py", message)
    
    def test_generate_smart_commit_message_multiple_files(self):
        """Test commit message generation with multiple file changes"""
        for i in range(3):
            with open(f"file_{i}.txt", "w") as f:
                f.write(f"Content {i}")
        
        message = self.service._generate_smart_commit_message()
        self.assertIn("Auto-save", message)
        self.assertIn("3", message)  # Should mention number of files
    
    def test_determine_file_action_new_file(self):
        """Test determining action for new file"""
        with open("brand_new_file.txt", "w") as f:
            f.write("New content")
        
        action = self.service._determine_file_action("brand_new_file.txt")
        self.assertEqual(action, "added")
    
    def test_determine_file_action_existing_file(self):
        """Test determining action for existing file"""
        # Modify existing file
        with open("README.md", "a") as f:
            f.write("\nAdditional content")
        
        action = self.service._determine_file_action("README.md")
        self.assertEqual(action, "updated")
    
    @patch('subprocess.run')
    def test_ensure_wip_branch_creates_new(self, mock_run):
        """Test WIP branch creation when it doesn't exist"""
        # Mock git branch list to return empty (no WIP branch)
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=0),  # git branch --list
            MagicMock(returncode=0),  # git checkout -b
        ]
        
        self.service._ensure_wip_branch()
        
        # Should call git checkout -b
        mock_run.assert_any_call(
            ["git", "checkout", "-b", "auto-wip"],
            cwd=self.test_dir,
            check=True
        )
    
    @patch('subprocess.run')
    def test_ensure_wip_branch_switches_to_existing(self, mock_run):
        """Test switching to existing WIP branch"""
        # Mock git branch list to return WIP branch exists
        mock_run.side_effect = [
            MagicMock(stdout="  auto-wip", returncode=0),  # git branch --list
            MagicMock(stdout="main", returncode=0),  # git rev-parse --abbrev-ref HEAD
            MagicMock(returncode=0),  # git checkout
        ]
        
        self.service._ensure_wip_branch()
        
        # Should call git checkout
        mock_run.assert_any_call(
            ["git", "checkout", "auto-wip"],
            cwd=self.test_dir,
            check=True
        )
    
    @patch('subprocess.run')
    def test_commit_and_push_success(self, mock_run):
        """Test successful commit and push"""
        mock_run.return_value = MagicMock(returncode=0)
        
        self.service._commit_and_push("Test commit message")
        
        # Should call git add, commit, and push
        expected_calls = [
            ["git", "add", "."],
            ["git", "commit", "-m", "Test commit message"],
            ["git", "push", "-u", "origin", "auto-wip"]
        ]
        
        for expected_call in expected_calls:
            mock_run.assert_any_call(
                expected_call,
                cwd=self.test_dir,
                check=True
            )
    
    def test_service_start_stop(self):
        """Test service start and stop functionality"""
        self.assertFalse(self.service.is_running)
        
        self.service.start()
        self.assertTrue(self.service.is_running)
        self.assertIsNotNone(self.service.thread)
        
        self.service.stop()
        self.assertFalse(self.service.is_running)
    
    @patch.object(AutoCommitService, '_auto_commit_if_changes')
    def test_force_commit_now(self, mock_commit):
        """Test force commit functionality"""
        mock_commit.return_value = None
        
        result = self.service.force_commit_now()
        self.assertTrue(result)
        mock_commit.assert_called_once()
    
    @patch.object(AutoCommitService, '_auto_commit_if_changes')
    def test_force_commit_now_with_error(self, mock_commit):
        """Test force commit with error"""
        mock_commit.side_effect = Exception("Test error")
        
        result = self.service.force_commit_now()
        self.assertFalse(result)
    
    def test_get_changed_files_with_changes(self):
        """Test getting list of changed files"""
        # Create some files
        with open("changed1.txt", "w") as f:
            f.write("Content 1")
        with open("changed2.py", "w") as f:
            f.write("print('hello')")
        
        changed_files = self.service._get_changed_files()
        
        self.assertIn("changed1.txt", changed_files)
        self.assertIn("changed2.py", changed_files)
    
    def test_integration_auto_commit_with_changes(self):
        """Integration test: auto-commit with actual changes"""
        # Create a test file
        with open("integration_test.txt", "w") as f:
            f.write("Integration test content")
        
        # Mock the push operation to avoid network calls
        with patch('subprocess.run') as mock_run:
            def side_effect(cmd, **kwargs):
                if cmd[:2] == ["git", "push"]:
                    return MagicMock(returncode=0)
                else:
                    # Execute actual git commands for everything else
                    return subprocess.run(cmd, **kwargs)
            
            mock_run.side_effect = side_effect
            
            # This should detect changes and perform auto-commit
            self.service._auto_commit_if_changes()
            
            # Verify push was called
            mock_run.assert_any_call(
                ["git", "push", "-u", "origin", "auto-wip"],
                cwd=self.test_dir,
                check=True
            )


if __name__ == "__main__":
    unittest.main()