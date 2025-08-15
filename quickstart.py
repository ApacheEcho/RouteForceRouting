#!/usr/bin/env python3
"""
Quick Start Script for RouteForce Routing

This script provides common development tasks in one place.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: str, description: str = "") -> bool:
    """Run a shell command and return success status"""
    if description:
        print(f"🔧 {description}")

    print(f"   Running: {cmd}")

    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=False
        )
        print(f"✅ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        return False


def check_env_file() -> bool:
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your configuration")
        return False
    return True


def setup_database():
    """Set up the database"""
    print("\n🗄️  Setting up database...")

    if not check_env_file():
        return False

    # Check if migrations directory exists
    if not os.path.exists("migrations"):
        run_command("flask db init", "Initializing database migrations")

    # Create migration
    run_command(
        "flask db migrate -m 'Initial migration'", "Creating migration"
    )

    # Apply migration
    run_command("flask db upgrade", "Applying migration")

    return True


def run_development_server():
    """Run the development server"""
    print("\n🚀 Starting development server...")

    if not check_env_file():
        return False

    # Set development environment
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "true"

    print("   Server will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")

    # Try different ways to run the server
    if os.path.exists("app.py"):
        run_command("python3 app.py", "Starting with app.py")
    elif os.path.exists("run_app.py"):
        run_command("python3 run_app.py", "Starting with run_app.py")
    else:
        run_command("flask run", "Starting with flask run")


def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")

    test_commands = [
        "python3 -m pytest tests/ -v",
        "python3 -m pytest . -k test_ -v",
        "find . -name 'test_*.py' -exec python3 {} \\;",
    ]

    for cmd in test_commands:
        if run_command(cmd, f"Trying: {cmd}"):
            break
    else:
        print(
            "❌ No test runner worked. Make sure tests are set up correctly."
        )


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")

    if os.path.exists("requirements.txt"):
        run_command(
            "pip3 install -r requirements.txt",
            "Installing from requirements.txt",
        )
    else:
        print("❌ requirements.txt not found")
        return False

    # Optional: Install development dependencies
    if os.path.exists("requirements-dev.txt"):
        run_command(
            "pip3 install -r requirements-dev.txt",
            "Installing development dependencies",
        )

    return True


def lint_code():
    """Run code linting"""
    print("\n🔍 Running code quality checks...")

    # Try different linters
    linters = [
        ("flake8 .", "Flake8 linting"),
        ("black --check .", "Black code formatting check"),
        ("pylint app/", "Pylint analysis"),
        ("mypy app/", "MyPy type checking"),
    ]

    for cmd, description in linters:
        try:
            subprocess.run(cmd.split(), check=True, capture_output=True)
            print(f"✅ {description} passed")
        except subprocess.CalledProcessError:
            print(f"⚠️  {description} found issues")
        except FileNotFoundError:
            print(f"ℹ️  {description} not available (tool not installed)")


def format_code():
    """Format code with black and isort"""
    print("\n🎨 Formatting code...")

    formatters = [
        ("black .", "Black code formatting"),
        ("isort .", "Import sorting"),
    ]

    for cmd, description in formatters:
        try:
            subprocess.run(cmd.split(), check=True)
            print(f"✅ {description} completed")
        except subprocess.CalledProcessError:
            print(f"❌ {description} failed")
        except FileNotFoundError:
            print(
                f"ℹ️  {description} not available (install with: pip install {cmd.split()[0]})"
            )


def run_security_scan():
    """Run security scanning with bandit"""
    print("\n🔒 Running security scan...")

    try:
        subprocess.run(["bandit", "-r", "app/"], check=True)
        print("✅ Security scan completed")
    except subprocess.CalledProcessError:
        print("⚠️  Security issues found")
    except FileNotFoundError:
        print("ℹ️  Bandit not available (install with: pip install bandit)")


def show_status():
    """Show project status"""
    print("\n📊 Project Status")
    print("=" * 50)

    # Check key files
    files_to_check = [
        (".env", "Environment configuration"),
        ("app/config.py", "Application configuration"),
        ("requirements.txt", "Dependencies list"),
        ("migrations/", "Database migrations"),
        ("uploads/", "Upload directory"),
        ("logs/", "Log directory"),
    ]

    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} (missing)")

    # Show environment
    env = os.environ.get("FLASK_ENV", "not set")
    print(f"\n🌍 Environment: {env}")

    # Show git status
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            print(f"📝 Git: Changes detected")
        else:
            print(f"📝 Git: Working directory clean")
    except:
        print(f"📝 Git: Not available or not a git repository")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="RouteForce Routing Development Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 quickstart.py --setup-db        # Set up database
  python3 quickstart.py --run             # Start development server
  python3 quickstart.py --test            # Run tests
  python3 quickstart.py --install         # Install dependencies
  python3 quickstart.py --status          # Show project status
        """,
    )

    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Set up the database (init, migrate, upgrade)",
    )
    parser.add_argument(
        "--run", action="store_true", help="Start the development server"
    )
    parser.add_argument(
        "--test", action="store_true", help="Run the test suite"
    )
    parser.add_argument(
        "--install", action="store_true", help="Install Python dependencies"
    )
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code with black and isort",
    )
    parser.add_argument(
        "--security", action="store_true", help="Run security scan"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show project status"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run setup, install, setup-db, lint, test",
    )

    args = parser.parse_args()

    # Change to project directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)

    print("🚀 RouteForce Routing Development Helper")
    print(f"📁 Working directory: {project_root}")

    if args.all:
        print("\n🔄 Running complete setup...")
        install_dependencies()
        setup_database()
        lint_code()
        run_tests()
        show_status()
    elif args.install:
        install_dependencies()
    elif args.setup_db:
        setup_database()
    elif args.run:
        run_development_server()
    elif args.test:
        run_tests()
    elif args.lint:
        lint_code()
    elif args.format:
        format_code()
    elif args.security:
        run_security_scan()
    elif args.status:
        show_status()
    else:
        # Interactive mode
        print("\nSelect an action:")
        print("1. Install dependencies")
        print("2. Set up database")
        print("3. Run development server")
        print("4. Run tests")
        print("5. Show status")
        print("6. Exit")

        try:
            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                install_dependencies()
            elif choice == "2":
                setup_database()
            elif choice == "3":
                run_development_server()
            elif choice == "4":
                run_tests()
            elif choice == "5":
                show_status()
            elif choice == "6":
                print("👋 Goodbye!")
            else:
                print("❌ Invalid choice")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
