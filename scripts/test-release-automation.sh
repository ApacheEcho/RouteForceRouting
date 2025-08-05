#!/bin/bash

# Test script to validate the release automation setup
# This script tests various components without creating actual releases

set -e

echo "🧪 Testing Release Automation Setup"
echo "=================================="

# Test 1: Version file exists and is readable
echo "📝 Testing version management..."
if [ -f "VERSION" ]; then
    VERSION=$(cat VERSION)
    echo "✅ VERSION file exists: $VERSION"
else
    echo "❌ VERSION file missing"
    exit 1
fi

# Test 2: App version import
echo "📦 Testing app version import..."
PYTHON_VERSION=$(python -c "from app import __version__; print(__version__)")
if [ "$PYTHON_VERSION" = "$VERSION" ]; then
    echo "✅ App version matches VERSION file: $PYTHON_VERSION"
else
    echo "❌ Version mismatch: VERSION=$VERSION, APP=$PYTHON_VERSION"
    exit 1
fi

# Test 3: Setup.py version
echo "⚙️  Testing setup.py version..."
SETUP_VERSION=$(python setup.py --version)
if [ "$SETUP_VERSION" = "$VERSION" ]; then
    echo "✅ Setup.py version matches: $SETUP_VERSION"
else
    echo "❌ Setup.py version mismatch: $SETUP_VERSION"
    exit 1
fi

# Test 4: Release script validation
echo "🚀 Testing release script..."
if [ -x "scripts/release.sh" ]; then
    # Test help
    ./scripts/release.sh --help > /dev/null
    echo "✅ Release script help works"
    
    # Test dry run
    ./scripts/release.sh --dry-run --force 0.1.1 > /dev/null
    echo "✅ Release script dry run works"
else
    echo "❌ Release script not executable"
    exit 1
fi

# Test 5: Workflow YAML validation
echo "🔧 Testing workflow syntax..."
if python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" 2>/dev/null; then
    echo "✅ Release workflow YAML is valid"
else
    echo "❌ Release workflow YAML has syntax errors"
    exit 1
fi

# Test 6: Documentation exists
echo "📚 Testing documentation..."
for doc in "CHANGELOG.md" "docs/RELEASE_AUTOMATION.md"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc exists"
    else
        echo "❌ $doc missing"
        exit 1
    fi
done

# Test 7: App still imports correctly
echo "🏗️  Testing app functionality..."
if python -c "from app import create_app; app = create_app('testing'); print('App factory OK')" 2>/dev/null; then
    echo "✅ App factory still works"
else
    echo "❌ App import broken"
    exit 1
fi

echo ""
echo "🎉 All release automation tests passed!"
echo ""
echo "To create your first release:"
echo "  ./scripts/release.sh 0.1.0"
echo ""
echo "To test workflow (requires push to GitHub):"
echo "  git tag v0.1.0-test"
echo "  git push origin v0.1.0-test"
echo "  # Then delete: git tag -d v0.1.0-test && git push origin --delete v0.1.0-test"