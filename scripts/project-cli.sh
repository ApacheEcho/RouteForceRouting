#!/bin/bash

# RouteForce Project CLI
# Usage: ./project-cli.sh [command]

case "$1" in
  "sprint-summary")
    gh issue list --milestone "Sprint 1" --json number,title,labels,assignees \
      --jq '.[] | "\(.number): \(.title) [\(.labels[].name)] @\(.assignees[].login)"'
    ;;
  
  "add-task")
    gh issue create --title "$2" --label "task" --milestone "Sprint 1"
    ;;
  
  "block")
    gh issue edit "$2" --add-label "blocked"
    gh issue comment "$2" --body "Blocked by #$3"
    ;;
  
  "velocity")
    echo "Calculating velocity..."
    gh issue list --state closed --milestone "Sprint 1" --json labels \
      --jq '[.[] | .labels[] | select(.name | startswith("sp:")) | .name[3:] | tonumber] | add'
    ;;
  
  *)
    echo "Commands: sprint-summary, add-task, block, velocity"
    ;;
esac
