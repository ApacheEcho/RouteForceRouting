#!/bin/bash
echo "Auto-commit started!"
while true; do
  sleep 600
  git add -A
  git commit -m "auto-save: $(date)" || echo "Nothing to commit"
  git push || echo "Push failed"
done
