#!/usr/bin/env python3
"""
GitHub Agents Utility Script
Provides local testing and management of GitHub Agents functionality
"""

import json
import os
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class GitHubAgentsManager:
    """Manager for GitHub Agents functionality"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.github_dir = self.project_root / ".github"
        self.workflows_dir = self.github_dir / "workflows"
        
    def check_setup(self) -> Dict[str, bool]:
        """Check if GitHub Agents are properly set up"""
        checks = {
            "copilot_config": (self.github_dir / "copilot.yml").exists(),
            "ai_workflow": (self.workflows_dir / "ai-coding-assistant.yml").exists(),
            "agents_workflow": (self.workflows_dir / "automated-code-agents.yml").exists(),
            "documentation": (self.github_dir / "GITHUB_AGENTS_SETUP.md").exists(),
            "python_env": self._check_python_dependencies(),
        }
        
        return checks
    
    def _check_python_dependencies(self) -> bool:
        """Check if required Python packages are installed"""
        required = ["black", "isort", "bandit", "safety", "radon"]
        try:
            for pkg in required:
                subprocess.run([sys.executable, "-c", f"import {pkg}"], 
                             check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, ImportError):
            return False
    
    def install_dependencies(self) -> bool:
        """Install required Python dependencies"""
        packages = [
            "black", "isort", "autoflake", "pyupgrade", 
            "bandit", "safety", "radon", "vulture",
            "pytest-benchmark", "memory-profiler"
        ]
        
        try:
            print("📦 Installing GitHub Agents dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade"
            ] + packages, check=True)
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def run_local_analysis(self, analysis_type: str, target_dir: str = "app/") -> bool:
        """Run local code analysis similar to GitHub Agents"""
        target_path = self.project_root / target_dir
        
        if not target_path.exists():
            print(f"❌ Target directory {target_dir} not found")
            return False
        
        print(f"🔍 Running {analysis_type} analysis on {target_dir}...")
        
        if analysis_type == "security":
            return self._run_security_analysis(target_path)
        elif analysis_type == "performance":
            return self._run_performance_analysis(target_path)
        elif analysis_type == "maintenance":
            return self._run_maintenance_analysis(target_path)
        elif analysis_type == "all":
            success = True
            success &= self._run_security_analysis(target_path)
            success &= self._run_performance_analysis(target_path)
            success &= self._run_maintenance_analysis(target_path)
            return success
        else:
            print(f"❌ Unknown analysis type: {analysis_type}")
            return False
    
    def _run_security_analysis(self, target_path: Path) -> bool:
        """Run security analysis using Bandit and Safety"""
        try:
            print("🛡️ Running security analysis...")
            
            # Bandit security scan
            bandit_result = subprocess.run([
                "bandit", "-r", str(target_path), "-f", "json"
            ], capture_output=True, text=True)
            
            if bandit_result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                bandit_data = json.loads(bandit_result.stdout) if bandit_result.stdout else {}
                issues = bandit_data.get("results", [])
                
                print(f"🔍 Bandit found {len(issues)} potential security issues")
                
                # Group by severity
                high = [i for i in issues if i.get("issue_severity") == "HIGH"]
                medium = [i for i in issues if i.get("issue_severity") == "MEDIUM"] 
                low = [i for i in issues if i.get("issue_severity") == "LOW"]
                
                print(f"  🔴 High: {len(high)}")
                print(f"  🟡 Medium: {len(medium)}")
                print(f"  🟢 Low: {len(low)}")
                
                if high:
                    print("\n🚨 High Severity Issues:")
                    for issue in high[:3]:  # Show top 3
                        print(f"  - {issue.get('filename', 'Unknown')}:{issue.get('line_number', '?')} - {issue.get('issue_text', 'No description')}")
            
            # Safety dependency scan
            print("\n🔒 Checking dependencies for vulnerabilities...")
            safety_result = subprocess.run([
                "safety", "check", "--json"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if safety_result.returncode == 0:
                print("✅ No known security vulnerabilities in dependencies")
            else:
                print("⚠️ Some dependency vulnerabilities found - check Safety output")
            
            return True
            
        except FileNotFoundError:
            print("❌ Security tools not installed. Run 'install-deps' first.")
            return False
        except Exception as e:
            print(f"❌ Security analysis failed: {e}")
            return False
    
    def _run_performance_analysis(self, target_path: Path) -> bool:
        """Run performance analysis"""
        try:
            print("⚡ Running performance analysis...")
            
            # Unused code detection
            print("🔍 Detecting unused code...")
            vulture_result = subprocess.run([
                "vulture", str(target_path), "--min-confidence", "70"
            ], capture_output=True, text=True)
            
            if vulture_result.stdout.strip():
                lines = vulture_result.stdout.strip().split('\n')
                print(f"📊 Found {len(lines)} potential unused code items")
                if lines:
                    print("  Top items:")
                    for line in lines[:5]:
                        print(f"    {line}")
            else:
                print("✅ No unused code detected")
            
            # Code complexity analysis
            print("\n🔍 Analyzing code complexity...")
            radon_result = subprocess.run([
                "radon", "cc", str(target_path), "--show-complexity"
            ], capture_output=True, text=True)
            
            if radon_result.stdout:
                lines = [l for l in radon_result.stdout.split('\n') if l.strip()]
                complex_functions = [l for l in lines if any(grade in l for grade in ['C', 'D', 'E', 'F'])]
                
                if complex_functions:
                    print(f"⚠️ Found {len(complex_functions)} complex functions:")
                    for func in complex_functions[:3]:
                        print(f"    {func}")
                else:
                    print("✅ All functions have acceptable complexity")
            
            return True
            
        except FileNotFoundError:
            print("❌ Performance analysis tools not installed. Run 'install-deps' first.")
            return False
        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")
            return False
    
    def _run_maintenance_analysis(self, target_path: Path) -> bool:
        """Run maintenance analysis"""
        try:
            print("🧹 Running maintenance analysis...")
            
            # Check code formatting
            print("🔍 Checking code formatting...")
            black_result = subprocess.run([
                "black", "--check", "--diff", str(target_path)
            ], capture_output=True, text=True)
            
            if black_result.returncode == 0:
                print("✅ Code is properly formatted")
            else:
                print("⚠️ Code formatting issues found")
                if black_result.stdout:
                    lines = black_result.stdout.split('\n')
                    changed_files = [l for l in lines if l.startswith('would reformat')]
                    print(f"  Files needing formatting: {len(changed_files)}")
            
            # Check import sorting
            print("\n🔍 Checking import organization...")
            isort_result = subprocess.run([
                "isort", "--check-only", "--diff", str(target_path)
            ], capture_output=True, text=True)
            
            if isort_result.returncode == 0:
                print("✅ Imports are properly organized")
            else:
                print("⚠️ Import organization issues found")
            
            return True
            
        except FileNotFoundError:
            print("❌ Maintenance tools not installed. Run 'install-deps' first.")
            return False
        except Exception as e:
            print(f"❌ Maintenance analysis failed: {e}")
            return False
    
    def apply_maintenance_fixes(self, target_dir: str = "app/") -> bool:
        """Apply automatic maintenance fixes"""
        target_path = self.project_root / target_dir
        
        if not target_path.exists():
            print(f"❌ Target directory {target_dir} not found")
            return False
        
        try:
            print(f"🔧 Applying maintenance fixes to {target_dir}...")
            
            # Format code with Black
            print("🎨 Formatting code with Black...")
            subprocess.run([
                "black", str(target_path)
            ], check=True)
            
            # Sort imports with isort
            print("📋 Organizing imports with isort...")
            subprocess.run([
                "isort", str(target_path)
            ], check=True)
            
            # Remove unused imports
            print("🧹 Removing unused imports...")
            for py_file in target_path.rglob("*.py"):
                subprocess.run([
                    "autoflake", "--in-place", "--remove-all-unused-imports", str(py_file)
                ], check=True)
            
            print("✅ Maintenance fixes applied successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to apply maintenance fixes: {e}")
            return False
        except FileNotFoundError:
            print("❌ Maintenance tools not installed. Run 'install-deps' first.")
            return False
    
    def generate_report(self, output_file: str = "agents_report.md") -> bool:
        """Generate comprehensive agents status report"""
        try:
            checks = self.check_setup()
            
            report = f"""# 🤖 GitHub Agents Status Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Project:** RouteForce Routing

## 📊 Setup Status

"""
            
            for check, status in checks.items():
                emoji = "✅" if status else "❌"
                name = check.replace("_", " ").title()
                report += f"- {emoji} **{name}**: {'Configured' if status else 'Not configured'}\n"
            
            report += f"""

## 🎯 Configuration Summary

- **Copilot**: {'Enabled' if checks['copilot_config'] else 'Disabled'}
- **AI Workflows**: {'Active' if checks['ai_workflow'] else 'Inactive'}
- **Automated Agents**: {'Active' if checks['agents_workflow'] else 'Inactive'}
- **Python Dependencies**: {'Installed' if checks['python_env'] else 'Missing'}

## 📋 Available Commands

```bash
# Check setup status
python github_agents.py status

# Install dependencies
python github_agents.py install-deps

# Run local analysis
python github_agents.py analyze security app/
python github_agents.py analyze performance app/
python github_agents.py analyze maintenance app/
python github_agents.py analyze all app/

# Apply maintenance fixes
python github_agents.py fix app/

# Generate this report
python github_agents.py report
```

## 🔗 Quick Links

- [GitHub Agents Setup Guide](.github/GITHUB_AGENTS_SETUP.md)
- [AI Coding Assistant Workflow](.github/workflows/ai-coding-assistant.yml)
- [Automated Code Agents Workflow](.github/workflows/automated-code-agents.yml)
- [Copilot Configuration](.github/copilot.yml)

---
*Report generated by GitHub Agents Manager*
"""
            
            with open(output_file, 'w') as f:
                f.write(report)
            
            print(f"📄 Report generated: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate report: {e}")
            return False


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="GitHub Agents Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Check agents setup status')
    
    # Install dependencies command
    subparsers.add_parser('install-deps', help='Install required dependencies')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run local analysis')
    analyze_parser.add_argument('type', choices=['security', 'performance', 'maintenance', 'all'],
                               help='Type of analysis to run')
    analyze_parser.add_argument('target', nargs='?', default='app/',
                               help='Target directory to analyze')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Apply maintenance fixes')
    fix_parser.add_argument('target', nargs='?', default='app/',
                           help='Target directory to fix')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate status report')
    report_parser.add_argument('--output', default='agents_report.md',
                              help='Output file for the report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = GitHubAgentsManager()
    
    # Execute commands
    if args.command == 'status':
        print("🔍 Checking GitHub Agents setup...")
        checks = manager.check_setup()
        
        print("\n📊 Setup Status:")
        all_good = True
        for check, status in checks.items():
            emoji = "✅" if status else "❌"
            name = check.replace("_", " ").title()
            print(f"  {emoji} {name}")
            if not status:
                all_good = False
        
        if all_good:
            print("\n🎉 All GitHub Agents are properly configured!")
        else:
            print("\n⚠️ Some components need configuration. See setup guide.")
    
    elif args.command == 'install-deps':
        manager.install_dependencies()
    
    elif args.command == 'analyze':
        manager.run_local_analysis(args.type, args.target)
    
    elif args.command == 'fix':
        manager.apply_maintenance_fixes(args.target)
    
    elif args.command == 'report':
        manager.generate_report(args.output)


if __name__ == "__main__":
    main()
