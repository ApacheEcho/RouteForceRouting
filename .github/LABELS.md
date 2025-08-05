# GitHub Labels Documentation

This document describes the comprehensive GitHub label system for the RouteForceRouting repository.

## Overview

Our label system is organized into four main categories to provide clear organization and efficient project management:

- **Priority**: Indicates the urgency and importance of issues
- **Type**: Categorizes the nature of the work required
- **Status**: Tracks the current state of work
- **Component**: Identifies which part of the system is affected

## Label Categories

### Priority Labels

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `priority:critical` | ![#B60205](https://via.placeholder.com/15/B60205/000000?text=+) | Critical priority - immediate attention required | Security vulnerabilities, production outages |
| `priority:high` | ![#D93F0B](https://via.placeholder.com/15/D93F0B/000000?text=+) | High priority - should be addressed soon | Important features, significant bugs |
| `priority:medium` | ![#FFA500](https://via.placeholder.com/15/FFA500/000000?text=+) | Medium priority - normal timeline | Regular features, minor improvements |
| `priority:low` | ![#FBCA04](https://via.placeholder.com/15/FBCA04/000000?text=+) | Low priority - can be addressed later | Nice-to-have features, documentation updates |

### Type Labels

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `type:bug` | ![#D73A4A](https://via.placeholder.com/15/D73A4A/000000?text=+) | Something isn't working correctly | Error reports, incorrect behavior |
| `type:feature` | ![#0075CA](https://via.placeholder.com/15/0075CA/000000?text=+) | New feature or functionality | Feature requests, new capabilities |
| `type:enhancement` | ![#A2EEEF](https://via.placeholder.com/15/A2EEEF/000000?text=+) | Improvement to existing functionality | UX improvements, performance optimizations |
| `type:documentation` | ![#0052CC](https://via.placeholder.com/15/0052CC/000000?text=+) | Documentation updates or improvements | README updates, API docs, guides |
| `type:security` | ![#7057FF](https://via.placeholder.com/15/7057FF/000000?text=+) | Security-related issue or improvement | Vulnerabilities, security enhancements |
| `type:performance` | ![#006B75](https://via.placeholder.com/15/006B75/000000?text=+) | Performance optimization or issue | Slow queries, memory leaks, optimization |
| `type:refactoring` | ![#5319E7](https://via.placeholder.com/15/5319E7/000000?text=+) | Code refactoring without functional changes | Code cleanup, architecture improvements |
| `type:maintenance` | ![#EDEDED](https://via.placeholder.com/15/EDEDED/000000?text=+) | Maintenance tasks and dependency updates | Library updates, build improvements |

### Status Labels

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `status:triage` | ![#FFFFFF](https://via.placeholder.com/15/FFFFFF/000000?text=+) | Issue needs to be triaged and categorized | New issues awaiting review |
| `status:in-progress` | ![#F9D0C4](https://via.placeholder.com/15/F9D0C4/000000?text=+) | Work is currently being done on this issue | Active development |
| `status:review` | ![#0E8A16](https://via.placeholder.com/15/0E8A16/000000?text=+) | Ready for code review | Pull requests awaiting review |
| `status:blocked` | ![#B60205](https://via.placeholder.com/15/B60205/000000?text=+) | Cannot proceed due to external dependencies | Waiting for external resources |
| `status:ready-for-merge` | ![#0E8A16](https://via.placeholder.com/15/0E8A16/000000?text=+) | Approved and ready to be merged | Final approval before merge |
| `status:on-hold` | ![#FBCA04](https://via.placeholder.com/15/FBCA04/000000?text=+) | Work temporarily paused | Deprioritized or pending decisions |

### Component Labels

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `component:backend` | ![#1D76DB](https://via.placeholder.com/15/1D76DB/000000?text=+) | Backend/API related changes | Server-side code, databases |
| `component:frontend` | ![#0E8A16](https://via.placeholder.com/15/0E8A16/000000?text=+) | Frontend/UI related changes | Web interface, user experience |
| `component:mobile` | ![#FF69B4](https://via.placeholder.com/15/FF69B4/000000?text=+) | Mobile app related changes | iOS, Android, React Native |
| `component:api` | ![#006B75](https://via.placeholder.com/15/006B75/000000?text=+) | API design or implementation | REST endpoints, GraphQL |
| `component:database` | ![#8B4513](https://via.placeholder.com/15/8B4513/000000?text=+) | Database schema or queries | Schema changes, data migrations |
| `component:devops` | ![#C5DEF5](https://via.placeholder.com/15/C5DEF5/000000?text=+) | CI/CD, deployment, infrastructure | GitHub Actions, Docker, deployment |
| `component:testing` | ![#F7E018](https://via.placeholder.com/15/F7E018/000000?text=+) | Testing infrastructure or test cases | Unit tests, integration tests |
| `component:routing` | ![#FFA500](https://via.placeholder.com/15/FFA500/000000?text=+) | Route optimization algorithms | Core routing logic |
| `component:analytics` | ![#8A2BE2](https://via.placeholder.com/15/8A2BE2/000000?text=+) | Analytics and monitoring features | Metrics, dashboards |

### Special Labels

| Label | Color | Description | Usage |
|-------|-------|-------------|-------|
| `good-first-issue` | ![#7057FF](https://via.placeholder.com/15/7057FF/000000?text=+) | Good for newcomers to the project | Beginner-friendly issues |
| `help-wanted` | ![#159818](https://via.placeholder.com/15/159818/000000?text=+) | Looking for contributors to help with this | Community contribution requests |
| `duplicate` | ![#CFD3D7](https://via.placeholder.com/15/CFD3D7/000000?text=+) | This issue or pull request already exists | Duplicate issues |
| `wontfix` | ![#FFFFFF](https://via.placeholder.com/15/FFFFFF/000000?text=+) | This will not be worked on | Issues that won't be addressed |
| `question` | ![#D876E3](https://via.placeholder.com/15/D876E3/000000?text=+) | Further information is requested | Support requests, clarifications |

## Usage Guidelines

### Label Assignment

1. **Every issue should have exactly one label from each relevant category:**
   - One Priority label (required)
   - One Type label (required)
   - One Status label (required)
   - One or more Component labels (as needed)

2. **Example combinations:**
   - `priority:high` + `type:bug` + `status:triage` + `component:backend`
   - `priority:medium` + `type:feature` + `status:in-progress` + `component:frontend` + `component:api`

### Workflow Integration

The labels integrate with our project automation:

- **Kanban Board**: Status labels determine which column issues appear in
- **Priority Sorting**: Priority labels control issue ordering
- **Auto-assignment**: Component labels can trigger automatic reviewer assignment
- **Filtering**: All labels support advanced filtering and searching

### Label Management

Labels are managed through:

1. **Configuration**: `.github/labels.yml` defines all labels
2. **Automation**: GitHub Action automatically applies label changes
3. **Script**: `scripts/standardize_labels.py` can be run manually
4. **Validation**: Regular checks ensure label consistency

### Migration from Legacy Labels

The following legacy labels are automatically replaced:

- `enhancement` → `type:enhancement`
- `triage` → `status:triage`
- `high-priority` → `priority:high`
- `medium-priority` → `priority:medium`

## Best Practices

1. **Be Consistent**: Always use the standardized labels
2. **Update Status**: Move issues through status labels as work progresses
3. **Multiple Components**: Use multiple component labels when changes affect multiple areas
4. **Priority Review**: Regularly review and adjust priorities during planning
5. **Clear Descriptions**: Use issue descriptions to provide context beyond labels

## Automation Features

Our label system includes several automated features:

- **Auto-triage**: New issues get `status:triage` automatically
- **Priority detection**: Issues with "critical" or "urgent" in the title get `priority:critical`
- **Blocking detection**: Comments mentioning "blocked by #" add `status:blocked`
- **Component assignment**: Component labels can trigger automatic reviewer assignment

## Maintenance

To update the label system:

1. Modify `.github/labels.yml`
2. Test changes with `python scripts/standardize_labels.py --validate-only`
3. Apply changes by pushing to main branch (triggers automation)
4. Update this documentation as needed

For questions or suggestions about the label system, please create an issue with the `type:question` label.