#!/bin/bash
# Example MCP shell context script for RouteForceRouting
# Outputs a summary of the project and recent git activity

echo "Project: RouteForceRouting"
echo "Owner: ApacheEcho"
echo "Date: $(date)"
echo "\nRecent Git Commits:"
git log --oneline -n 5 || echo "(git log unavailable)"
echo "\nPython Files:"
find . -name '*.py' | head -n 10
