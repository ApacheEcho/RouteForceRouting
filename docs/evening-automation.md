# Evening Automation

This directory contains the evening automation system for RouteForceRouting development workflow.

## Overview

The evening automation runs daily at **5:45 PM UTC** to prepare the development environment for productive coding at 6:00 PM.

## Components

### 🔧 evening-automation.yml
GitHub Actions workflow that:
- **Syncs morning changes** - Fetches latest changes and checks for conflicts
- **Runs test suite** - Executes pytest with coverage reporting
- **Prepares workspace** - Cleans up artifacts and prepares environment
- **Generates priorities** - Analyzes current state and creates recommendations

### 📊 evening_priorities.py
Python script that analyzes:
- Git repository status (branch, uncommitted changes, conflicts)
- Recent test results and coverage
- TODO items in codebase
- Recent file changes
- Generates actionable recommendations for evening development

## Usage

### Automatic Execution
The workflow runs automatically at 5:45 PM UTC every day via cron schedule.

### Manual Execution
Trigger manually via GitHub Actions:
```bash
# Go to Actions tab in GitHub
# Select "Evening Automation" workflow
# Click "Run workflow"
```

### Local Testing
Run the priorities script locally:
```bash
python scripts/evening_priorities.py
```

## Output

### Generated Files
- `evening_priorities.json` - Structured analysis and recommendations
- `evening_summary.md` - Human-readable workflow summary
- `test-results/` - Test results and coverage reports

### Example Priorities Output
```json
{
  "generated_at": "2025-08-05T17:45:00.000000",
  "session_type": "evening_development",
  "git_status": {
    "branch": "main",
    "uncommitted_changes": false,
    "unpushed_commits": false
  },
  "recommendations": [
    "🎯 Focus on high-priority features",
    "📊 Review performance metrics",
    "🔍 Code review pending PRs"
  ]
}
```

## Benefits

✅ **Consistent Environment** - Workspace is always clean and ready  
✅ **No Context Switching** - Priorities and status ready at 6 PM  
✅ **Early Issue Detection** - Test failures and conflicts identified  
✅ **Actionable Insights** - Specific recommendations for evening work  
✅ **Productivity Boost** - Jump straight into coding without setup  

## Customization

### Schedule
Edit the cron expression in `evening-automation.yml`:
```yaml
schedule:
  - cron: '45 17 * * *'  # 5:45 PM UTC
```

### Timezone Adjustment
For different timezones:
- **EST**: Use '45 22 * * *' (5:45 PM EST = 10:45 PM UTC)
- **PST**: Use '45 1 * * *' (5:45 PM PST = 1:45 AM UTC next day)
- **CET**: Use '45 16 * * *' (5:45 PM CET = 4:45 PM UTC)

### Recommendations
Modify the recommendation logic in `scripts/evening_priorities.py` to customize analysis and suggestions.

## Troubleshooting

### Workflow Fails
1. Check GitHub Actions logs
2. Verify Python dependencies
3. Check file permissions on scripts
4. Ensure GitHub token has required permissions

### Missing Priorities
1. Verify script runs without errors locally
2. Check if scripts directory exists
3. Ensure script has executable permissions

### Schedule Issues
1. Remember GitHub uses UTC time
2. Verify cron syntax
3. Check if repository has recent activity (inactive repos may pause schedules)

## Integration

The evening automation integrates with:
- **CI/CD Pipeline** - Leverages existing test infrastructure
- **Morning Automation** - Complements morning prep workflow
- **Development Workflow** - Seamlessly fits into daily coding routine

Ready for productive evening development! 🌅