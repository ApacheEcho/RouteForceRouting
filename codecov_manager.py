#!/usr/bin/env python3
"""
CodeCov Setup and Management Utility for RouteForce Routing

This script provides comprehensive CodeCov integration management,
including local testing, configuration validation, and coverage analysis.

Usage:
    python codecov_manager.py --setup          # Initial CodeCov setup
    python codecov_manager.py --test           # Run tests with coverage
    python codecov_manager.py --validate       # Validate configuration
    python codecov_manager.py --report         # Generate coverage report
    python codecov_manager.py --upload         # Upload to CodeCov (CI only)
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
import time
from typing import Dict, List, Optional


class CodeCovManager:
    """Manages CodeCov integration and coverage analysis."""

    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.coverage_threshold = 70
        self.codecov_config = self.root_dir / "codecov.yml"
        self.coverage_config = self.root_dir / ".coveragerc"
        self.pytest_config = self.root_dir / "pytest.ini"

    def setup_codecov(self):
        """Initial CodeCov setup and configuration."""
        print("🚀 Setting up CodeCov integration for RouteForce Routing")

        # Check if configuration files exist
        configs = {
            "CodeCov Config": self.codecov_config,
            "Coverage Config": self.coverage_config,
            "PyTest Config": self.pytest_config,
        }

        print("\n📋 Configuration Files:")
        for name, path in configs.items():
            status = "✅ Found" if path.exists() else "❌ Missing"
            print(f"  {name}: {status}")

        # Install required packages
        print("\n📦 Installing coverage dependencies...")
        required_packages = [
            "coverage[toml]>=7.6.0",
            "pytest-cov>=6.0.0",
            "pytest-html>=4.1.0",
            "pytest-json-report>=2.2.0",
            "pytest-benchmark>=5.1.0",
        ]

        for package in required_packages:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    check=True,
                    capture_output=True,
                )
                print(f"  ✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"  ❌ Failed to install {package}")

        # Create test directory if it doesn't exist
        test_dir = self.root_dir / "tests"
        if not test_dir.exists():
            test_dir.mkdir()
            print(f"✅ Created tests directory: {test_dir}")

        print("\n🎯 CodeCov setup complete!")
        print("Next steps:")
        print("1. Sign up at https://codecov.io and connect your repository")
        print("2. Add CODECOV_TOKEN to your GitHub repository secrets")
        print("3. Run 'python codecov_manager.py --test' to verify setup")

    def validate_configuration(self):
        """Validate CodeCov and coverage configuration."""
        print("🔍 Validating CodeCov configuration...")

        validation_results = []

        # Check codecov.yml
        if self.codecov_config.exists():
            try:
                import yaml

                with open(self.codecov_config, "r") as f:
                    config = yaml.safe_load(f)

                # Validate key sections
                if "coverage" in config:
                    validation_results.append(
                        "✅ CodeCov coverage section found"
                    )
                else:
                    validation_results.append(
                        "❌ CodeCov coverage section missing"
                    )

                if "comment" in config:
                    validation_results.append(
                        "✅ CodeCov comment configuration found"
                    )
                else:
                    validation_results.append(
                        "⚠️  CodeCov comment configuration missing"
                    )

            except Exception as e:
                validation_results.append(
                    f"❌ CodeCov config validation failed: {e}"
                )
        else:
            validation_results.append("❌ codecov.yml not found")

        # Check .coveragerc
        if self.coverage_config.exists():
            validation_results.append("✅ Coverage configuration found")
        else:
            validation_results.append("❌ .coveragerc not found")

        # Check pytest.ini
        if self.pytest_config.exists():
            try:
                with open(self.pytest_config, "r") as f:
                    content = f.read()
                if "--cov=" in content:
                    validation_results.append("✅ PyTest coverage enabled")
                else:
                    validation_results.append(
                        "❌ PyTest coverage not configured"
                    )
            except Exception as e:
                validation_results.append(
                    f"❌ PyTest config validation failed: {e}"
                )
        else:
            validation_results.append("❌ pytest.ini not found")

        # Print results
        print("\n📋 Validation Results:")
        for result in validation_results:
            print(f"  {result}")

        # Overall status
        failed_checks = [r for r in validation_results if r.startswith("❌")]
        if not failed_checks:
            print("\n✅ All configuration validations passed!")
            return True
        else:
            print(f"\n❌ {len(failed_checks)} validation(s) failed")
            return False

    def run_tests_with_coverage(self, test_type: str = "all"):
        """Run tests with comprehensive coverage analysis."""
        print(f"🧪 Running {test_type} tests with coverage analysis...")

        # Prepare coverage command
        base_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-report=json:coverage.json",
            "--cov-config=.coveragerc",
            "--cov-branch",
            f"--cov-fail-under={self.coverage_threshold}",
            "--html=reports/pytest_report.html",
            "--json-report",
            "--json-report-file=reports/pytest_report.json",
            "-v",
        ]

        # Add test type specific options
        if test_type == "unit":
            base_cmd.extend(["-m", "unit"])
        elif test_type == "integration":
            base_cmd.extend(["-m", "integration"])
        elif test_type == "api":
            base_cmd.extend(["-m", "api"])
        elif test_type == "algorithm":
            base_cmd.extend(["-m", "algorithm"])
        elif test_type == "fast":
            base_cmd.extend(["-m", "not slow and not external"])

        # Add test paths
        test_dir = self.root_dir / "tests"
        if test_dir.exists():
            base_cmd.append(str(test_dir))

        # Create reports directory
        reports_dir = self.root_dir / "reports"
        reports_dir.mkdir(exist_ok=True)

        # Run tests
        print(f"🏃‍♂️ Executing: {' '.join(base_cmd)}")

        try:
            start_time = time.time()
            result = subprocess.run(base_cmd, capture_output=True, text=True)
            execution_time = time.time() - start_time

            print(
                f"\n⏱️  Test execution completed in {execution_time:.2f} seconds"
            )
            print(f"📊 Exit code: {result.returncode}")

            if result.stdout:
                print("\n📄 Test Output:")
                print(result.stdout)

            if result.stderr and result.returncode != 0:
                print("\n⚠️  Error Output:")
                print(result.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False

    def generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        print("📊 Generating comprehensive coverage report...")

        try:
            # Generate text report
            print("\n📋 Coverage Summary:")
            subprocess.run(
                [sys.executable, "-m", "coverage", "report", "--show-missing"],
                check=True,
            )

            # Generate JSON report for analysis
            subprocess.run(
                [sys.executable, "-m", "coverage", "json", "--pretty-print"],
                check=True,
            )

            # Load and analyze JSON report
            coverage_file = self.root_dir / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, "r") as f:
                    data = json.load(f)

                total_coverage = data["totals"]["percent_covered"]
                covered_lines = data["totals"]["covered_lines"]
                total_lines = data["totals"]["num_statements"]
                missing_lines = data["totals"]["missing_lines"]

                print(f"\n📈 Coverage Analysis:")
                print(f"  Total Coverage: {total_coverage:.2f}%")
                print(f"  Lines Covered: {covered_lines:,}")
                print(f"  Total Lines: {total_lines:,}")
                print(f"  Missing Lines: {missing_lines:,}")

                # Coverage by file
                print(f"\n📁 Coverage by File:")
                for filename, file_data in data["files"].items():
                    file_coverage = (
                        (
                            file_data["summary"]["covered_lines"]
                            / file_data["summary"]["num_statements"]
                            * 100
                        )
                        if file_data["summary"]["num_statements"] > 0
                        else 0
                    )
                    print(f"  {filename}: {file_coverage:.1f}%")

                # Quality assessment
                print(f"\n🎯 Quality Assessment:")
                if total_coverage >= 90:
                    print("  ✅ Excellent coverage (≥90%)")
                elif total_coverage >= 80:
                    print("  ✅ Good coverage (≥80%)")
                elif total_coverage >= 70:
                    print("  ⚠️  Acceptable coverage (≥70%)")
                elif total_coverage >= 50:
                    print("  ⚠️  Low coverage (≥50%)")
                else:
                    print("  ❌ Poor coverage (<50%)")

                return True
            else:
                print("❌ Coverage data not found")
                return False

        except Exception as e:
            print(f"❌ Coverage report generation failed: {e}")
            return False

    def upload_to_codecov(self):
        """Upload coverage data to CodeCov (for CI environments)."""
        print("☁️  Uploading coverage to CodeCov...")

        # Check if we're in CI environment
        ci_env = os.environ.get("CI")
        if not ci_env:
            print(
                "⚠️  Not in CI environment - CodeCov upload may require token"
            )

        # Check for CodeCov token
        codecov_token = os.environ.get("CODECOV_TOKEN")
        if not codecov_token and not ci_env:
            print("❌ CODECOV_TOKEN environment variable not set")
            return False

        try:
            # Upload using codecov CLI or curl
            cmd = ["codecov"]
            if codecov_token:
                cmd.extend(["-t", codecov_token])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Coverage successfully uploaded to CodeCov")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"❌ CodeCov upload failed: {result.stderr}")
                return False

        except FileNotFoundError:
            print(
                "⚠️  CodeCov CLI not found, trying alternative upload method..."
            )
            # Alternative upload using curl (simplified)
            return False
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False

    def cleanup_coverage_files(self):
        """Clean up coverage artifacts."""
        print("🧹 Cleaning up coverage files...")

        cleanup_paths = [
            ".coverage",
            ".coverage.*",
            "htmlcov/",
            "coverage.xml",
            "coverage.json",
            "reports/",
        ]

        for path_pattern in cleanup_paths:
            if "*" in path_pattern:
                # Handle glob patterns
                import glob

                for path in glob.glob(path_pattern):
                    try:
                        if os.path.isdir(path):
                            import shutil

                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                        print(f"  🗑️  Removed {path}")
                    except Exception:
                        pass
            else:
                path = Path(path_pattern)
                try:
                    if path.is_dir():
                        import shutil

                        shutil.rmtree(path)
                    elif path.exists():
                        path.unlink()
                    print(f"  🗑️  Removed {path}")
                except Exception:
                    pass


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="CodeCov Setup and Management for RouteForce Routing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python codecov_manager.py --setup              # Initial setup
  python codecov_manager.py --test               # Run all tests
  python codecov_manager.py --test unit          # Run unit tests only
  python codecov_manager.py --validate           # Validate configuration
  python codecov_manager.py --report             # Generate coverage report
  python codecov_manager.py --upload             # Upload to CodeCov
  python codecov_manager.py --cleanup            # Clean coverage files
        """,
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Initial CodeCov setup and configuration",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate CodeCov configuration",
    )
    parser.add_argument(
        "--test",
        nargs="?",
        const="all",
        choices=["all", "unit", "integration", "api", "algorithm", "fast"],
        help="Run tests with coverage (default: all)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive coverage report",
    )
    parser.add_argument(
        "--upload", action="store_true", help="Upload coverage to CodeCov"
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up coverage artifacts"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=70,
        help="Coverage threshold percentage (default: 70)",
    )

    args = parser.parse_args()

    manager = CodeCovManager()
    manager.coverage_threshold = args.threshold

    if args.setup:
        manager.setup_codecov()
    elif args.validate:
        success = manager.validate_configuration()
        sys.exit(0 if success else 1)
    elif args.test:
        success = manager.run_tests_with_coverage(args.test)
        if success:
            manager.generate_coverage_report()
        sys.exit(0 if success else 1)
    elif args.report:
        success = manager.generate_coverage_report()
        sys.exit(0 if success else 1)
    elif args.upload:
        success = manager.upload_to_codecov()
        sys.exit(0 if success else 1)
    elif args.cleanup:
        manager.cleanup_coverage_files()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
