#!/bin/bash

# PR Lint Script for RouteForcePro
# Usage: bash scripts/lint-pr.sh <pull_request_file.md>

FILE=$1

echo "🔍 Linting PR: $FILE"

# Check for required fields
grep -q "## Linked Issue" "$FILE" || echo "❌ Missing 'Linked Issue' section"
grep -q "## Test Evidence" "$FILE" || echo "❌ Missing 'Test Evidence'"
grep -q "## Deployment Impact" "$FILE" || echo "❌ Missing 'Deployment Impact'"
grep -q "AI-generated?" "$FILE" || echo "❌ Missing 'AI-generated?' field"

# Suggest commit format
echo "🔎 Checking commit format..."
COMMITS=$(git log --format=%s -n 5)
echo "$COMMITS" | grep -Ev "^(feat|fix|chore|refactor|test):" && echo "⚠️  Use standard commit prefixes"

echo "✅ PR lint complete"