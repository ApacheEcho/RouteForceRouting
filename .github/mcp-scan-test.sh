#!/usr/bin/env bash
set -euo pipefail
# Simple local scanner test harness for MCP model usage detection
# Usage: ./ .github/mcp-scan-test.sh [changed-files-list]
FILES_LIST=${1:-changed.txt}
if [ ! -s "$FILES_LIST" ]; then
  echo "No changed files list found at $FILES_LIST"
  exit 1
fi
models_regex='(copilot/gpt-5-mini-preview|copilot/gpt-4.1)|\b(chat\.mcp\.modelPreferences|chat\.mcp\.serverSampling)\b'
# produce filtered file list
FILES=$(grep -Ev "^\.github/workflows/" "$FILES_LIST" || true)
FILES=$(echo "$FILES" | grep -E "\.(py|js|ts|json|yaml|yml|md|txt|ini|cfg|env)$" || true)
if [ -z "$FILES" ]; then
  echo "No candidate files after filtering"
  exit 0
fi
echo "Files to scan:\n$FILES"
found=false
while IFS= read -r f || [ -n "$f" ]; do
  if [ -z "$f" ]; then
    continue
  fi
  if [ -f "$f" ]; then
    matches=$(grep -En "${models_regex}" "$f" || true)
    if [ -n "$matches" ]; then
      echo "Match found in: $f"
      echo "$matches"
      found=true
      break
    fi
  fi
done <<< "$FILES"
if [ "$found" = true ]; then
  echo "FOUND=true"
  exit 0
else
  echo "FOUND=false"
  exit 0
fi
