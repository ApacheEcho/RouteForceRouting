#!/usr/bin/env python3
"""
Initial Configuration Setup for RouteForce Routing

This script helps you set up your RouteForce Routing project with the necessary
configuration files and environment setup.
"""

import os
import shutil
import sys
from pathlib import Path


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_step(step: str) -> None:
    """Print a formatted step"""
    print(f"\n🔧 {step}")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"✅ {message}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"⚠️  {message}")


def print_info(message: str) -> None:
    """Print an info message"""
    print(f"ℹ️  {message}")


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return os.path.exists(filepath)


def create_env_file() -> None:
    """Create .env file from .env.example if it doesn't exist"""
    print_step("Setting up environment file...")

    if check_file_exists(".env"):
        print_warning(".env file already exists, skipping...")
        return

    if check_file_exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print_success("Created .env file from .env.example")
        print_info("Edit .env file to configure your settings")
    else:
        print_warning(
            ".env.example not found, you'll need to create .env manually"
        )


def create_directories() -> None:
    """Create necessary directories"""
    print_step("Creating necessary directories...")

    directories = [
        "uploads",
        "logs",
        "temp",
        "data",
        "backups",
        "codeql-results",
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print_success(f"Created directory: {directory}/")
        else:
            print_info(f"Directory already exists: {directory}/")


def setup_git_hooks() -> None:
    """Set up useful git hooks"""
    print_step("Setting up Git hooks...")

    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        print_warning("No .git directory found, skipping git hooks setup")
        return

    # Pre-commit hook for basic checks
    pre_commit_hook = hooks_dir / "pre-commit"
    if not pre_commit_hook.exists():
        hook_content = """#!/bin/sh
# RouteForce Routing pre-commit hook
# Runs basic checks before committing

echo "🔍 Running pre-commit checks..."

# Check for large files
git diff --cached --name-only | while read file; do
    if [ -f "$file" ] && [ $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null) -gt 10485760 ]; then
        echo "❌ Error: File $file is larger than 10MB"
        exit 1
    fi
done

# Check for common secrets patterns
if git diff --cached --name-only | xargs grep -l "SECRET_KEY.*=" 2>/dev/null | grep -v ".env.example" | grep -v "config.py"; then
    echo "⚠️  Warning: Potential secret key found in staged files"
    echo "   Make sure you're not committing actual secret keys!"
fi

echo "✅ Pre-commit checks passed"
"""
        with open(pre_commit_hook, "w") as f:
            f.write(hook_content)
        os.chmod(pre_commit_hook, 0o755)
        print_success("Created pre-commit git hook")
    else:
        print_info("Pre-commit hook already exists")


def check_requirements() -> None:
    """Check if requirements are installed"""
    print_step("Checking Python dependencies...")

    try:
        import flask

        print_success("Flask is installed")
    except ImportError:
        print_warning("Flask not found - run: pip install -r requirements.txt")

    try:
        import sqlalchemy

        print_success("SQLAlchemy is installed")
    except ImportError:
        print_warning(
            "SQLAlchemy not found - run: pip install -r requirements.txt"
        )


def display_next_steps() -> None:
    """Display next steps for the user"""
    print_header("🚀 SETUP COMPLETE!")

    print(
        """
Next steps to get RouteForce Routing running:

1. Configure your environment:
   📝 Edit .env file with your settings (database, API keys, etc.)

2. Set up your database:
   🗄️  flask db init        # Initialize migrations
   🗄️  flask db migrate     # Create migration
   🗄️  flask db upgrade     # Apply migration

3. Install dependencies (if not done):
   📦 pip install -r requirements.txt

4. Get Google Maps API key:
   🗺️  Visit: https://console.cloud.google.com/apis/credentials
   🗺️  Add your API key to .env file: GOOGLE_MAPS_API_KEY=your-key-here

5. Run the application:
   ▶️  python app.py        # Development server
   ▶️  flask run            # Alternative way

6. Access the application:
   🌐 http://localhost:5000

7. Optional - Set up production environment:
   🐳 Use docker-compose.yml for containerized deployment
   ☁️  Configure environment variables for your platform

Important files to review:
📄 .env                    - Environment configuration
📄 app/config.py          - Application settings
📄 docker-compose.yml     - Container setup
📄 requirements.txt       - Python dependencies

For more information, check the documentation in the project files.
"""
    )


def main():
    """Main setup function"""
    print_header("RouteForce Routing - Initial Setup")
    print("This script will help you set up your RouteForce Routing project.")

    # Change to project directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    # Run setup steps
    create_env_file()
    create_directories()
    setup_git_hooks()
    check_requirements()

    # Display completion message
    display_next_steps()


if __name__ == "__main__":
    main()
