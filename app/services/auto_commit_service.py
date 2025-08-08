#!/usr/bin/env python3
"""
Auto-commit background service

Implements automatic git operations every 10 minutes with smart commit messages.
Ensures no code is ever lost by continuously backing up changes to a WIP branch.
"""

import logging
import os
import subprocess
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AutoCommitService:
    """
    Background service that automatically commits and pushes code changes
    every 10 minutes to prevent any code loss.
    """

    def __init__(self, repo_path: str = None, interval_minutes: int = 10):
        self.repo_path = repo_path or os.getcwd()
        self.interval_seconds = interval_minutes * 60
        self.wip_branch = "auto-wip"
        self.is_running = False
        self.thread = None
        self.last_commit_hash = None

    def start(self):
        """Start the background auto-commit service"""
        if self.is_running:
            logger.info("Auto-commit service is already running")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._run_service, daemon=True)
        self.thread.start()
        logger.info(
            f"Auto-commit service started with {self.interval_seconds}s interval"
        )

    def stop(self):
        """Stop the background auto-commit service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Auto-commit service stopped")

    def _run_service(self):
        """Main service loop - runs every 10 minutes"""
        while self.is_running:
            try:
                self._auto_commit_if_changes()
            except Exception as e:
                logger.error(f"Auto-commit error: {e}")

            # Sleep for the interval, but check every second if we should stop
            for _ in range(self.interval_seconds):
                if not self.is_running:
                    break
                time.sleep(1)

    def _auto_commit_if_changes(self):
        """Check for changes and auto-commit if any exist"""
        if not self._has_git_changes():
            logger.debug("No changes detected, skipping auto-commit")
            return

        logger.info("Changes detected, performing auto-commit")

        # Ensure we're on the WIP branch
        self._ensure_wip_branch()

        # Generate smart commit message
        commit_message = self._generate_smart_commit_message()

        # Perform the commit and push
        self._commit_and_push(commit_message)

        logger.info(f"Auto-commit completed: {commit_message}")

    def _has_git_changes(self) -> bool:
        """Check if there are any uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return len(result.stdout.strip()) > 0
        except subprocess.CalledProcessError:
            logger.error("Failed to check git status")
            return False

    def _ensure_wip_branch(self):
        """Ensure we're working on the WIP branch"""
        try:
            # Check if WIP branch exists
            result = subprocess.run(
                ["git", "branch", "--list", self.wip_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            if not result.stdout.strip():
                # Create WIP branch from current branch
                subprocess.run(
                    ["git", "checkout", "-b", self.wip_branch],
                    cwd=self.repo_path,
                    check=True,
                )
                logger.info(f"Created WIP branch: {self.wip_branch}")
            else:
                # Switch to WIP branch if not already on it
                current_branch = self._get_current_branch()
                if current_branch != self.wip_branch:
                    subprocess.run(
                        ["git", "checkout", self.wip_branch],
                        cwd=self.repo_path,
                        check=True,
                    )
                    logger.info(f"Switched to WIP branch: {self.wip_branch}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to ensure WIP branch: {e}")

    def _get_current_branch(self) -> str:
        """Get the current git branch name"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"

    def _generate_smart_commit_message(self) -> str:
        """Generate a smart commit message based on file changes"""
        try:
            # Get list of changed files
            changed_files = self._get_changed_files()

            # Get diff statistics
            diff_stats = self._get_diff_stats()

            # Generate message based on changes
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if len(changed_files) == 1:
                file_name = os.path.basename(changed_files[0])
                action = self._determine_file_action(changed_files[0])
                message = f"Auto-save: {action} {file_name}"
            elif len(changed_files) <= 5:
                file_names = [os.path.basename(f) for f in changed_files]
                message = f"Auto-save: Updated {', '.join(file_names)}"
            else:
                message = f"Auto-save: Updated {len(changed_files)} files"

            # Add statistics
            if diff_stats:
                message += f" (+{diff_stats['insertions']} -{diff_stats['deletions']})"

            message += f" [{timestamp}]"

            return message

        except Exception as e:
            logger.error(f"Failed to generate smart commit message: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"Auto-save: Backup changes [{timestamp}]"

    def _get_changed_files(self) -> list[str]:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            staged_result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            untracked_result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            files = set()
            files.update(
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )
            files.update(
                staged_result.stdout.strip().split("\n")
                if staged_result.stdout.strip()
                else []
            )
            files.update(
                untracked_result.stdout.strip().split("\n")
                if untracked_result.stdout.strip()
                else []
            )

            return [f for f in files if f]

        except subprocess.CalledProcessError:
            return []

    def _get_diff_stats(self) -> dict[str, int] | None:
        """Get diff statistics (insertions, deletions)"""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat", "--staged", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the last line which contains summary like "3 files changed, 15 insertions(+), 2 deletions(-)"
            lines = result.stdout.strip().split("\n")
            if lines and "changed" in lines[-1]:
                stats_line = lines[-1]
                insertions = 0
                deletions = 0

                if "insertion" in stats_line:
                    import re

                    match = re.search(r"(\d+) insertion", stats_line)
                    if match:
                        insertions = int(match.group(1))

                if "deletion" in stats_line:
                    import re

                    match = re.search(r"(\d+) deletion", stats_line)
                    if match:
                        deletions = int(match.group(1))

                return {"insertions": insertions, "deletions": deletions}

        except subprocess.CalledProcessError:
            pass

        return None

    def _determine_file_action(self, file_path: str) -> str:
        """Determine what kind of action was performed on a file"""
        try:
            # Check if file is new
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return "added"

            # Check if file was deleted
            if not os.path.exists(os.path.join(self.repo_path, file_path)):
                return "deleted"

            # Default to modified
            return "updated"

        except Exception:
            return "modified"

    def _commit_and_push(self, message: str):
        """Commit all changes and push to WIP branch"""
        try:
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)

            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", message], cwd=self.repo_path, check=True
            )

            # Push to remote WIP branch
            subprocess.run(
                ["git", "push", "-u", "origin", self.wip_branch],
                cwd=self.repo_path,
                check=True,
            )

            logger.info(f"Successfully committed and pushed: {message}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to commit and push: {e}")
            raise

    def force_commit_now(self) -> bool:
        """Force an immediate commit regardless of timer"""
        try:
            self._auto_commit_if_changes()
            return True
        except Exception as e:
            logger.error(f"Force commit failed: {e}")
            return False


# Global service instance
_auto_commit_service = None


def get_auto_commit_service() -> AutoCommitService:
    """Get the global auto-commit service instance"""
    global _auto_commit_service
    if _auto_commit_service is None:
        _auto_commit_service = AutoCommitService()
    return _auto_commit_service


def start_auto_commit_service():
    """Start the auto-commit background service"""
    service = get_auto_commit_service()
    service.start()


def stop_auto_commit_service():
    """Stop the auto-commit background service"""
    service = get_auto_commit_service()
    service.stop()
