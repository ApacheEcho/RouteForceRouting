#!/bin/bash
# Project Automation Quick Setup Script
# This script helps initialize the project automation system

set -e

echo "🚀 RouteForce Project Automation Setup"
echo "======================================"

# Check if we're in the right directory
if [ ! -f ".github/workflows/project-automation.yml" ]; then
    echo "❌ Error: Must be run from the repository root directory"
    echo "   Make sure you're in the RouteForceRouting directory"
    exit 1
fi

echo "📁 Repository structure looks good!"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required"
    echo "   Please install Python 3 and try again"
    exit 1
fi

echo "🐍 Python 3 found"

# Check for required dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import requests" &> /dev/null; then
    echo "📥 Installing requests library..."
    python3 -m pip install requests --user
fi

# Run automation tests
echo "🧪 Running automation tests..."
python3 .github/test-automation.py

echo ""
echo "⚙️  Setup Options:"
echo ""
echo "1. Test automation logic (completed ✅)"
echo "2. Setup GitHub labels (requires GITHUB_TOKEN)"
echo "3. Validate workflow syntax"
echo "4. Show usage examples"
echo ""

# Setup labels if token is available
if [ -n "$GITHUB_TOKEN" ]; then
    echo "🏷️  GitHub token found - setting up labels..."
    python3 .github/setup-project-labels.py
else
    echo "ℹ️  To setup labels, run:"
    echo "   export GITHUB_TOKEN=your_token"
    echo "   python3 .github/setup-project-labels.py"
fi

echo ""
echo "📖 Usage Examples:"
echo ""
echo "Issue Status Commands (use in comments):"
echo "  /start or /in-progress  - Start working on issue"
echo "  /review or /ready       - Mark ready for review"
echo "  /done or /complete      - Close and mark done"
echo "  /todo or /backlog       - Move back to backlog"
echo ""
echo "Automatic Labeling Keywords:"
echo "  Priority: critical, urgent, security → high-priority"
echo "  Component: api, frontend, backend, docker → component labels"
echo "  Type: bug, feature, enhancement → type labels"
echo "  Effort: quick/simple → small, complex/major → large"
echo ""
echo "📋 Project Board Views Available:"
echo "  - Sprint Board (Kanban style)"
echo "  - Priority View (grouped by priority)"
echo "  - Component View (by technical area)"
echo "  - Effort Planning (by estimated effort)"
echo "  - Bug Tracking (dedicated bug workflow)"
echo ""
echo "✅ Project automation setup complete!"
echo ""
echo "Next steps:"
echo "1. Create/configure your GitHub project board"
echo "2. Update project URL in .github/workflows/project-automation.yml"
echo "3. Test with a sample issue"
echo "4. Review .github/PROJECT_README.md for full documentation"
echo ""
echo "🎉 Happy automating!"