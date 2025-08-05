# GitHub Labels System

This document describes the standardized GitHub labels system implemented for the RouteForce Routing project. The system provides comprehensive categorization using priority, type, status, and component labels.

## 🎯 Overview

The labels system is designed to:
- **Standardize** issue and PR categorization
- **Improve** project management and workflow
- **Enable** better filtering and automation
- **Maintain** consistency across the project

## 📋 Label Categories

### 🔥 Priority Labels
- `priority/critical` - Critical priority, immediate attention required (P0)
- `priority/high` - High priority, should be addressed soon (P1)  
- `priority/medium` - Medium priority, normal timeline (P2)
- `priority/low` - Low priority, when time permits (P3)

### 🏷️ Type Labels
- `type/bug` - Something isn't working
- `type/feature` - New feature or request
- `type/documentation` - Improvements or additions to documentation
- `type/refactor` - Code refactoring and improvements
- `type/performance` - Performance improvements
- `type/security` - Security related issues
- `type/testing` - Testing related changes

### 📊 Status Labels
- `status/triage` - Needs initial review and categorization
- `status/ready` - Ready to work on
- `status/in-progress` - Currently being worked on
- `status/review` - In review/waiting for review
- `status/blocked` - Blocked by external dependency
- `status/on-hold` - Work paused

### 🧩 Component Labels
- `component/routing` - Route optimization and algorithms
- `component/ui` - User interface and frontend
- `component/api` - API and backend services
- `component/database` - Database related changes
- `component/deployment` - Deployment and infrastructure
- `component/mobile` - Mobile application components
- `component/analytics` - Analytics and monitoring

### ⭐ Special Labels
- `good-first-issue` - Good for newcomers
- `help-wanted` - Extra attention is needed
- `duplicate` - This issue or pull request already exists
- `invalid` - This doesn't seem right
- `imported` - Auto-imported from external system
- `breaking-change` - This introduces breaking changes

## 🔧 Management Tools

### Scripts
- `scripts/manage_labels.py` - Main label management script
  - Validate configuration: `python scripts/manage_labels.py validate`
  - Sync labels: `python scripts/manage_labels.py sync`
  - Export documentation: `python scripts/manage_labels.py export`

### Automation
- `.github/workflows/sync-labels.yml` - Automatically syncs labels when configuration changes
- `.github/labels.yml` - Central configuration for all labels

## 📝 Usage Guidelines

### For Issues
1. **Always** assign a priority label (`priority/*`)
2. **Always** assign a type label (`type/*`)
3. **Start** with `status/triage` for new issues
4. **Add** relevant component labels as needed
5. **Update** status labels as work progresses

### For Pull Requests
1. **Add** type labels based on the change
2. **Add** component labels for affected areas
3. **Add** `breaking-change` if applicable
4. **Use** status labels to track review progress

### Label Combinations
Good examples:
- `priority/high` + `type/bug` + `component/routing` + `status/in-progress`
- `priority/medium` + `type/feature` + `component/ui` + `status/review`
- `priority/low` + `type/documentation` + `status/ready`

## 🔄 Workflow Integration

The labels integrate with:
- **Project boards** (see `.github/project-views.yml`)
- **Issue templates** (automatic label assignment)
- **GitHub Actions** (automated workflows)
- **Sprint planning** (filtering and organization)

## 🚀 Getting Started

1. **Contributors**: Use issue templates which automatically assign appropriate labels
2. **Maintainers**: Update labels as issues progress through workflow
3. **Project managers**: Use project boards with label-based filtering

## 📖 Full Documentation

For complete details including colors and aliases, see [LABELS.md](.github/LABELS.md).

## 🔄 Updates

To modify the label system:
1. Edit `.github/labels.yml`
2. Run `python scripts/manage_labels.py validate` to check configuration
3. The workflow will automatically sync labels when merged to main

---

*This labels system was implemented as part of [Issue #39](https://github.com/ApacheEcho/RouteForceRouting/issues/39) to standardize project management.*