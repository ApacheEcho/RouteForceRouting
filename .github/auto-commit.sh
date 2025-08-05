#!/bin/bash

# Auto-commit script with enhanced features
# Configurable variables
SLEEP_INTERVAL="${AUTO_COMMIT_INTERVAL:-600}"  # Default 10 minutes
COMMIT_PREFIX="${AUTO_COMMIT_PREFIX:-auto-save}"
LOG_FILE="${AUTO_COMMIT_LOG:-/tmp/auto-commit.log}"
MAX_PUSH_RETRIES="${AUTO_COMMIT_MAX_RETRIES:-3}"
RETRY_DELAY="${AUTO_COMMIT_RETRY_DELAY:-30}"

# Logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Network connectivity check
check_network_connectivity() {
    local test_hosts=("8.8.8.8" "1.1.1.1" "github.com")
    
    for host in "${test_hosts[@]}"; do
        if ping -c 1 -W 3 "$host" >/dev/null 2>&1; then
            log_message "DEBUG" "Network connectivity confirmed via $host"
            return 0
        fi
    done
    
    log_message "WARN" "No network connectivity detected"
    return 1
}

# Check for uncommitted changes
has_uncommitted_changes() {
    # Check for staged changes, unstaged changes, or untracked files
    if ! git diff-index --quiet HEAD --; then
        return 0  # Has staged changes
    fi
    
    if [ -n "$(git ls-files --others --exclude-standard)" ]; then
        return 0  # Has untracked files
    fi
    
    return 1  # No changes
}

# Git push with retry logic
push_with_retry() {
    local attempt=1
    local max_attempts="$MAX_PUSH_RETRIES"
    
    while [ $attempt -le "$max_attempts" ]; do
        log_message "INFO" "Push attempt $attempt of $max_attempts"
        
        if git push 2>&1 | tee -a "$LOG_FILE"; then
            log_message "INFO" "Push successful on attempt $attempt"
            return 0
        else
            local exit_code=$?
            log_message "ERROR" "Push failed on attempt $attempt (exit code: $exit_code)"
            
            if [ $attempt -lt "$max_attempts" ]; then
                log_message "INFO" "Waiting $RETRY_DELAY seconds before retry..."
                sleep "$RETRY_DELAY"
            fi
        fi
        
        ((attempt++))
    done
    
    log_message "ERROR" "Push failed after $max_attempts attempts"
    return 1
}

# Main execution
main() {
    log_message "INFO" "Auto-commit script started (PID: $$)"
    log_message "INFO" "Configuration: interval=${SLEEP_INTERVAL}s, prefix='$COMMIT_PREFIX', log='$LOG_FILE'"
    
    # Ensure we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_message "ERROR" "Not in a git repository. Exiting."
        exit 1
    fi
    
    while true; do
        log_message "DEBUG" "Checking for changes..."
        
        if has_uncommitted_changes; then
            log_message "INFO" "Changes detected, preparing commit"
            
            # Add all changes
            if git add -A 2>&1 | tee -a "$LOG_FILE"; then
                log_message "INFO" "Files staged successfully"
            else
                log_message "ERROR" "Failed to stage files"
                sleep "$SLEEP_INTERVAL"
                continue
            fi
            
            # Create commit
            local commit_message
            commit_message="$COMMIT_PREFIX: $(date '+%Y-%m-%d %H:%M:%S')"
            if git commit -m "$commit_message" 2>&1 | tee -a "$LOG_FILE"; then
                log_message "INFO" "Commit created: $commit_message"
                
                # Check network and push
                if check_network_connectivity; then
                    if ! push_with_retry; then
                        log_message "ERROR" "All push attempts failed"
                    fi
                else
                    log_message "WARN" "Skipping push due to network connectivity issues"
                fi
            else
                log_message "ERROR" "Failed to create commit"
            fi
        else
            log_message "DEBUG" "No changes detected"
        fi
        
        log_message "DEBUG" "Sleeping for $SLEEP_INTERVAL seconds..."
        sleep "$SLEEP_INTERVAL"
    done
}

# Handle script termination gracefully
cleanup() {
    log_message "INFO" "Auto-commit script terminated (PID: $$)"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start main execution
main "$@"
