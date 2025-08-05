#!/bin/bash

# Auto-commit script with improved error handling, logging, and configuration
# Environment variables:
# - AUTO_COMMIT_INTERVAL: Sleep interval in seconds (default: 600)
# - AUTO_COMMIT_MAX_RETRIES: Max retries for git push (default: 3)
# - AUTO_COMMIT_LOG_FILE: Log file path (default: /tmp/auto-commit.log)

set -euo pipefail

# Configuration with defaults
SLEEP_INTERVAL=${AUTO_COMMIT_INTERVAL:-600}
MAX_RETRIES=${AUTO_COMMIT_MAX_RETRIES:-3}
LOG_FILE=${AUTO_COMMIT_LOG_FILE:-/tmp/auto-commit.log}

# Logging function
log() {
    local level="$1"
    shift
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] $*" | tee -a "$LOG_FILE"
}

# Error handling function
handle_error() {
    log "ERROR" "Script failed at line $1"
    exit 1
}

# Signal handler for graceful exit
cleanup() {
    log "INFO" "Received termination signal, shutting down gracefully"
    exit 0
}

# Retry function for git push
retry_git_push() {
    local retries=0
    while [ $retries -lt "$MAX_RETRIES" ]; do
        if git push; then
            log "INFO" "Git push succeeded"
            return 0
        else
            retries=$((retries + 1))
            log "WARN" "Git push failed (attempt $retries/$MAX_RETRIES)"
            if [ $retries -lt "$MAX_RETRIES" ]; then
                log "INFO" "Retrying git push in 30 seconds..."
                sleep 30
            fi
        fi
    done
    log "ERROR" "Git push failed after $MAX_RETRIES attempts"
    return 1
}

# Check if git repository is clean
is_repo_clean() {
    [ -z "$(git status --porcelain)" ]
}

# Main execution
trap 'handle_error $LINENO' ERR
trap cleanup SIGINT SIGTERM

log "INFO" "Auto-commit started with interval ${SLEEP_INTERVAL}s, max retries: $MAX_RETRIES"
log "INFO" "Log file: $LOG_FILE"

while true; do
    log "INFO" "Sleeping for ${SLEEP_INTERVAL} seconds..."
    sleep "$SLEEP_INTERVAL"
    
    # Check if there are any changes to commit
    if is_repo_clean; then
        log "INFO" "No changes detected, skipping commit"
        continue
    fi
    
    log "INFO" "Changes detected, proceeding with auto-commit"
    
    # Stage all changes
    if git add -A; then
        log "INFO" "Successfully staged all changes"
    else
        log "ERROR" "Failed to stage changes"
        continue
    fi
    
    # Check again after staging (in case .gitignore filtered everything)
    if git diff --cached --quiet; then
        log "INFO" "No staged changes after applying .gitignore, skipping commit"
        continue
    fi
    
    # Commit changes
    commit_message="auto-save: $(date '+%Y-%m-%d %H:%M:%S')"
    if git commit -m "$commit_message"; then
        log "INFO" "Successfully committed changes: $commit_message"
    else
        log "ERROR" "Failed to commit changes"
        continue
    fi
    
    # Push changes with retry logic
    if retry_git_push; then
        log "INFO" "Auto-commit cycle completed successfully"
    else
        log "ERROR" "Failed to push changes after retries, continuing..."
    fi
done
