# Project Board Automation Documentation

This document describes the comprehensive project board automation setup for the RouteForceRouting repository.

## Overview

The project automation consists of several GitHub Actions workflows that automatically manage issues, pull requests, and project board items to streamline the development workflow.

## Automation Components

### 1. Basic Project Automation (`project-automation.yml`)

**Purpose**: Handles basic project board management and issue/PR triage.

**Triggers**:
- Issues: opened, closed, assigned, labeled, unlabeled
- Pull Requests: opened, closed, merged, ready_for_review, converted_to_draft
- Comments: created

**Key Features**:
- **Auto-add to Project**: Automatically adds new issues and PRs to the project board
- **Priority Detection**: Assigns priority labels based on keywords:
  - High: critical, urgent, security, breaking, crash, data loss
  - Medium: important, enhancement, feature  
  - Low: documentation, typo, cleanup, refactor
- **Component Detection**: Labels issues based on content keywords:
  - `component:backend`: api, backend, server, database, routing, algorithm
  - `component:frontend`: ui, frontend, interface, dashboard, css, html
  - `component:mobile`: mobile, ios, android, app
  - `component:ml`: machine learning, ml, genetic, optimization, algorithm
  - `component:infrastructure`: docker, deployment, ci, cd, infrastructure
- **Auto-assignment**: Assigns high-priority items to project owner
- **Milestone Assignment**: Automatically assigns issues to current sprint milestone

### 2. Advanced Project Automation (`advanced-project-automation.yml`)

**Purpose**: Provides sophisticated automation for complex workflows.

**Key Features**:
- **Comment-based Automation**:
  - "blocked by #" or "depends on #" → adds `blocked` label
  - "ready for review" → adds `review-requested` label
  - "wip" or "work in progress" → adds `in-progress` label
- **PR Review Automation**:
  - Approved reviews → adds `approved` label
  - Changes requested → adds `changes-requested` label
- **Type Detection**: Auto-labels based on title patterns:
  - `bug`: bug, fix, error, issue
  - `enhancement`: feature, enhancement, add, implement
  - `documentation`: doc, readme, documentation
  - `testing`: test, testing
  - `performance`: performance, optimization, speed, slow
  - `security`: security, vulnerability, auth, permission
- **Status Transitions**:
  - New issues → `status:backlog`
  - PR ready for review → `status:review`
  - PR converted to draft → `status:draft`, `in-progress`
  - Closed items → `status:done`
- **File-based Component Detection**: Analyzes changed files in PRs:
  - `app/`, `routing/`, `main.py` → `component:backend`
  - `frontend/`, `static/`, `.html`, `.css`, `.js` → `component:frontend`
  - `mobile/` → `component:mobile`
  - `test*`, `tests/` → `component:testing`
  - `docker*`, `.github/`, `k8s/`, `nginx/` → `component:infrastructure`
  - `genetic*`, `ml_*`, `optimization*` → `component:ml`
  - `README*`, `*.md`, `docs/` → `documentation`

### 3. Stale Issue Management (`stale-management.yml`)

**Purpose**: Automatically manages stale issues and PRs to keep the repository clean.

**Configuration**:
- **Schedule**: Runs daily at 1 AM UTC
- **Issue Stale Period**: 60 days
- **PR Stale Period**: 30 days  
- **Auto-close Period**: 30 days for issues, 14 days for PRs
- **Exempt Labels**: `keep-open`, `high-priority`, `security`, `blocked`, `pinned`

### 4. Label Setup (`setup-labels.yml`)

**Purpose**: Creates and maintains all required labels for the automation system.

**Label Categories**:

#### Priority Labels
- `high-priority` (🔴): High priority issues that need immediate attention
- `medium-priority` (🟠): Medium priority tasks  
- `low-priority` (🟢): Low priority tasks

#### Component Labels
- `component:backend` (🔵): Backend/API related issues
- `component:frontend` (🟣): Frontend/UI related issues
- `component:mobile` (🟡): Mobile app related issues
- `component:ml` (🌸): Machine learning/algorithms
- `component:infrastructure` (🟢): DevOps/Infrastructure
- `component:testing` (🟡): Testing related issues

#### Type Labels
- `bug` (🔴): Something is not working
- `enhancement` (🔵): New feature or request
- `documentation` (🔵): Improvements or additions to documentation
- `performance` (🔴): Performance improvements
- `security` (🔴): Security related issues

#### Status Labels
- `status:backlog` (🟣): Issues in the backlog
- `status:in-progress` (🟡): Work in progress
- `status:review` (🟣): Under review
- `status:done` (🟢): Completed
- `status:draft` (⚪): Draft pull request

#### Workflow Labels
- `blocked` (🔴): Blocked by dependencies
- `approved` (🟢): Approved for merge
- `changes-requested` (🟠): Changes requested
- `review-requested` (🔵): Review requested
- `stale` (🟤): Stale issue/PR
- `keep-open` (🟠): Prevent auto-closure
- `pinned` (🟣): Pinned issue

## Project Board Configuration

The project uses a Sprint Board layout with four columns:

### 1. Backlog
- **Filters**: `status:open`, `-label:in-progress`, `-label:review`
- **Purpose**: New and unassigned issues

### 2. In Progress  
- **Filters**: `status:open`, `label:in-progress`
- **Purpose**: Active work items

### 3. Review
- **Filters**: `status:open`, `label:review`  
- **Purpose**: Items awaiting review

### 4. Done
- **Filters**: `status:closed`
- **Purpose**: Completed items

## Workflow Integration

### For Issues
1. **Creation**: Auto-added to project board with `status:backlog`
2. **Labeling**: Auto-labeled based on title/content keywords
3. **Assignment**: High-priority items auto-assigned to owner
4. **Milestone**: Auto-assigned to current sprint
5. **Status**: Transitions through backlog → in-progress → review → done

### For Pull Requests
1. **Creation**: Auto-added to project board
2. **Component Detection**: Auto-labeled based on changed files
3. **Review Process**: Status updates based on review state
4. **Draft Handling**: Special handling for draft PRs
5. **Completion**: Auto-labeled as done when merged/closed

### For Comments
- **Dependency Tracking**: "blocked by #X" comments add blocked label
- **Status Updates**: "ready for review" updates status
- **Work Progress**: "WIP" comments track progress

## Testing

The automation includes comprehensive tests in `test_project_automation.py`:

- **Workflow Validation**: YAML syntax and structure
- **Configuration Testing**: Project views and permissions
- **Logic Testing**: Keyword detection and component mapping
- **Integration Testing**: Status transitions and automation flow

## Usage Examples

### Creating Issues
```markdown
Title: "Critical bug in route optimization algorithm"
Result: auto-labeled with high-priority, bug, component:ml, status:backlog
```

### Pull Request Automation
```markdown
PR changing files: ['app/main.py', 'routing/core.py'] 
Result: auto-labeled with component:backend
```

### Comment-based Control
```markdown
Comment: "This is blocked by #123"
Result: adds blocked label automatically
```

## Maintenance

### Adding New Labels
1. Update `setup-labels.yml` with new label definitions
2. Run the workflow manually or push changes to trigger auto-update

### Modifying Automation Rules  
1. Edit the appropriate workflow file
2. Test changes in a branch before merging
3. Monitor automation logs for issues

### Customizing Thresholds
- Stale periods: Edit `stale-management.yml`
- Priority keywords: Edit `project-automation.yml`
- Component mappings: Edit `advanced-project-automation.yml`

## Troubleshooting

### Common Issues
1. **Labels not being applied**: Check workflow logs and keyword matching
2. **Items not added to project**: Verify project URL and permissions
3. **Status not updating**: Check label transitions and filters

### Debugging
- Check GitHub Actions logs for workflow execution details
- Verify label existence using the setup-labels workflow
- Test individual automation rules with sample issues/PRs

## Security Considerations

- All workflows use minimal required permissions
- Secrets are properly scoped and secured
- Automation respects security-labeled items with special handling
- Stale automation exempts security issues from auto-closure

## Performance

- Workflows are optimized to run efficiently
- Batch operations reduce API calls
- Conditional execution prevents unnecessary runs
- Rate limiting respected through proper design

This automation system provides comprehensive project management capabilities while maintaining flexibility for manual overrides when needed.