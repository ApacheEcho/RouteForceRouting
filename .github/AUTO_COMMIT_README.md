# Enhanced Auto-Commit Script

This document describes the enhanced `auto-commit.sh` script located in `.github/auto-commit.sh`.

## Features

The enhanced auto-commit script provides the following improvements over the original version:

### 1. **Smart Change Detection**
- Only commits when there are actual changes to commit
- Checks for staged changes, unstaged changes, and untracked files
- Prevents unnecessary empty commits

### 2. **Network Connectivity Check**
- Verifies network connectivity before attempting to push
- Tests multiple hosts (8.8.8.8, 1.1.1.1, github.com) for reliability
- Skips push attempts when no network is available

### 3. **Comprehensive Logging**
- Logs all operations with timestamps
- Supports different log levels (DEBUG, INFO, WARN, ERROR)
- Configurable log file location
- Logs both to console and file for real-time monitoring

### 4. **Retry Logic for Push Operations**
- Automatically retries failed push operations
- Configurable maximum retry attempts
- Configurable delay between retries
- Detailed error reporting for failed pushes

### 5. **Configuration Options**
All behavior can be customized using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_COMMIT_INTERVAL` | 600 | Sleep interval in seconds between checks |
| `AUTO_COMMIT_PREFIX` | "auto-save" | Prefix for commit messages |
| `AUTO_COMMIT_LOG` | "/tmp/auto-commit.log" | Log file location |
| `AUTO_COMMIT_MAX_RETRIES` | 3 | Maximum push retry attempts |
| `AUTO_COMMIT_RETRY_DELAY` | 30 | Seconds to wait between push retries |

### 6. **Graceful Termination**
- Handles SIGTERM and SIGINT signals properly
- Logs termination events
- Clean shutdown process

## Usage

### Basic Usage
```bash
./.github/auto-commit.sh
```

### With Custom Configuration
```bash
# Set custom interval (5 minutes) and commit prefix
export AUTO_COMMIT_INTERVAL=300
export AUTO_COMMIT_PREFIX="automated-backup"
export AUTO_COMMIT_LOG="/var/log/auto-commit.log"

./.github/auto-commit.sh
```

### Running in Background
```bash
# Run in background with nohup
nohup ./.github/auto-commit.sh &

# Or using screen/tmux
screen -S auto-commit ./.github/auto-commit.sh
```

## Log Format

The script generates logs in the following format:
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] Message
```

Example log output:
```
[2025-08-05 14:30:00] [INFO] Auto-commit script started (PID: 12345)
[2025-08-05 14:30:00] [INFO] Configuration: interval=600s, prefix='auto-save', log='/tmp/auto-commit.log'
[2025-08-05 14:30:00] [DEBUG] Checking for changes...
[2025-08-05 14:30:00] [INFO] Changes detected, preparing commit
[2025-08-05 14:30:01] [INFO] Files staged successfully
[2025-08-05 14:30:01] [INFO] Commit created: auto-save: 2025-08-05 14:30:01
[2025-08-05 14:30:01] [DEBUG] Network connectivity confirmed via 8.8.8.8
[2025-08-05 14:30:01] [INFO] Push attempt 1 of 3
[2025-08-05 14:30:02] [INFO] Push successful on attempt 1
```

## Testing

A test script is provided to validate the functionality:

```bash
./test_auto_commit.sh
```

The test script validates:
- Script syntax
- Shellcheck compliance
- Logging functionality
- Network connectivity check
- Change detection logic

## Error Handling

The script handles various error conditions:

- **Network failures**: Skips push when network is unavailable
- **Git errors**: Logs detailed error information
- **Push failures**: Retries with exponential backoff
- **Permission issues**: Logs appropriate error messages

## Security Considerations

- The script only operates on the current git repository
- No sensitive information is logged
- Network connectivity tests use safe, public DNS servers
- All git operations use the repository's existing configuration

## Backward Compatibility

The enhanced script maintains full backward compatibility with the original version:
- Same basic functionality (auto-commit every 10 minutes by default)
- Same commit message format (when using defaults)
- No breaking changes to existing behavior

## Troubleshooting

### Common Issues

1. **Permission denied for log file**
   - Solution: Set `AUTO_COMMIT_LOG` to a writable location
   
2. **Push failures**
   - Check git remote configuration
   - Verify authentication credentials
   - Review network connectivity

3. **High CPU usage**
   - Increase `AUTO_COMMIT_INTERVAL` for less frequent checks
   - Monitor log file size and rotate if necessary

### Debug Mode

For troubleshooting, you can monitor the script's activity:

```bash
# Follow the log file in real-time
tail -f /tmp/auto-commit.log

# Run with verbose git output
export GIT_TRACE=1
./.github/auto-commit.sh
```