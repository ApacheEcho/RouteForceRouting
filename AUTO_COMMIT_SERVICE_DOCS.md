# Auto-Commit Service

## Overview

The Auto-Commit Service is a background automation process that automatically commits and pushes code changes every 10 minutes to prevent any code loss. This feature addresses Issue #51 requirements by providing:

- ✅ Auto-commit every 10 minutes
- ✅ Smart commit messages based on file changes
- ✅ Push to WIP (Work In Progress) branch
- ✅ Guarantee no code is lost - every single line is preserved
- ✅ No manual git commands necessary

## Features

### Background Service
- Runs continuously in the background as a daemon thread
- Automatically starts with Flask application
- Monitors repository for changes every 10 minutes (configurable)
- Thread-safe and production-ready

### Smart Commit Messages
The service generates intelligent commit messages based on the types of changes:
- Single file: `Auto-save: updated filename.py [timestamp]`
- Multiple files: `Auto-save: Updated file1.py, file2.js [timestamp]`
- Many files: `Auto-save: Updated 15 files (+50 -10) [timestamp]`
- Includes diff statistics when available

### WIP Branch Management
- Automatically creates and manages a `auto-wip` branch
- Switches to WIP branch for auto-commits
- Preserves original branch for manual work
- Pushes all changes to remote WIP branch

### Zero Code Loss
- Commits ALL changes including untracked files
- Never overwrites or loses any code
- Preserves file permissions and git metadata
- Graceful error handling with detailed logging

## Configuration

### Environment Variables

```bash
# Enable/disable the auto-commit service (default: true)
AUTO_COMMIT_ENABLED=true

# Commit interval in minutes (default: 10)
AUTO_COMMIT_INTERVAL_MINUTES=10

# WIP branch name (default: auto-wip)
AUTO_COMMIT_WIP_BRANCH=auto-wip
```

### Flask Integration

The service automatically starts with the Flask application:

```python
from app import create_app

app = create_app('development')  # Auto-commit service starts automatically
```

To disable for testing:
```python
import os
os.environ['AUTO_COMMIT_ENABLED'] = 'false'
app = create_app('development')
```

## CLI Management

Use the CLI tool for manual control:

```bash
# Check service status
python scripts/auto_commit_cli.py status

# Start service manually
python scripts/auto_commit_cli.py start

# Stop service
python scripts/auto_commit_cli.py stop

# Force immediate commit
python scripts/auto_commit_cli.py commit

# Test functionality
python scripts/auto_commit_cli.py test
```

## API Usage

For programmatic control:

```python
from app.services.auto_commit_service import get_auto_commit_service

# Get service instance
service = get_auto_commit_service()

# Force immediate commit
success = service.force_commit_now()

# Check if running
if service.is_running:
    print("Auto-commit service is active")
```

## File Structure

```
app/
├── services/
│   └── auto_commit_service.py    # Main service implementation
└── config.py                     # Configuration with auto-commit settings

scripts/
└── auto_commit_cli.py            # Command line interface

tests/
└── test_auto_commit_service.py   # Comprehensive test suite

demo_auto_commit.py               # Demo and example usage
```

## How It Works

1. **Initialization**: Service starts as daemon thread with Flask app
2. **Monitoring**: Every 10 minutes, checks for git changes using `git status --porcelain`
3. **Branch Management**: Ensures working on WIP branch (`auto-wip`)
4. **Change Detection**: Identifies new, modified, and deleted files
5. **Smart Messaging**: Generates descriptive commit message with statistics
6. **Commit Process**: 
   - `git add .` (includes untracked files)
   - `git commit -m "smart message"`
   - `git push -u origin auto-wip`
7. **Error Handling**: Logs errors but continues operation
8. **Repeat**: Sleeps until next interval

## Error Handling

- **Git Errors**: Logged but service continues
- **Network Issues**: Push failures are logged, commits are preserved locally
- **Branch Conflicts**: Automatically handles branch creation/switching
- **Partial Failures**: Individual operations failing don't stop the service

## Production Considerations

- Service runs as daemon thread (won't block main application)
- Minimal resource usage (only active during commit operations)
- Git operations use subprocess for reliability
- Thread-safe implementation for concurrent Flask applications
- Configurable intervals for different environments

## Testing

Run the comprehensive test suite:

```bash
# Run auto-commit specific tests
python -m pytest tests/test_auto_commit_service.py -v

# Test CLI functionality
python scripts/auto_commit_cli.py test

# Demo the service
python demo_auto_commit.py
```

## Security Notes

- Only commits to WIP branch (never affects main branches)
- Uses subprocess for git operations (no shell injection risks)
- Respects existing `.gitignore` files
- No sensitive data exposure in commit messages
- Local repository access only (no remote credentials handled)

## Troubleshooting

### Service Not Starting
- Check `AUTO_COMMIT_ENABLED` environment variable
- Verify git repository is properly initialized
- Check Flask application logs for error messages

### Commits Not Appearing
- Verify WIP branch exists: `git branch --list auto-wip`
- Check for git configuration: `git config user.name` and `git config user.email`
- Review service logs for push failures

### Performance Issues
- Increase interval: `AUTO_COMMIT_INTERVAL_MINUTES=15`
- Check repository size and number of files
- Monitor system resources during commit operations

## Implementation Notes

This implementation fulfills all requirements from Issue #51:

1. ✅ **Auto-commit every 10 minutes**: Configurable interval, default 10 minutes
2. ✅ **Smart commit messages**: Context-aware messages based on file changes
3. ✅ **Push to WIP branch**: Dedicated `auto-wip` branch for automatic commits
4. ✅ **Never lose code**: Commits ALL changes including untracked files
5. ✅ **No manual git commands**: Fully automated background service

The service integrates seamlessly with the existing Flask application and provides enterprise-grade reliability for code preservation.