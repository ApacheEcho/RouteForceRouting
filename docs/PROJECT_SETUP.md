# RouteForce GitHub Project Setup Guide

## Custom Fields Configuration

To add custom fields to your GitHub Project:

1. Go to your project board
2. Click ⚙️ Settings
3. Click "Custom fields"
4. Add these fields:

### Story Points (Number)
- **Name**: Story Points
- **Type**: Number
- **Description**: Estimated effort (1, 2, 3, 5, 8, 13)

### Sprint (Single Select)
- **Name**: Sprint
- **Type**: Single select
- **Options**: Sprint 1, Sprint 2, Sprint 3, Sprint 4

### Component (Single Select)
- **Name**: Component
- **Type**: Single select
- **Options**: Backend, Frontend, API, Database, DevOps

### Due Date (Date)
- **Name**: Due Date
- **Type**: Date

### Blocked By (Text)
- **Name**: Blocked By
- **Type**: Text
- **Description**: Issue numbers blocking this work

## Automation Rules

Add these automation rules in your project settings:

1. **Auto-add new issues**
   - When: Item added to project
   - Set: Status to "Backlog"

2. **Move to In Progress**
   - When: Item labeled with "in-progress"
   - Set: Status to "In Progress"

3. **Move to Done**
   - When: Item closed
   - Set: Status to "Done"

## Using the Project CLI

```bash
# View current sprint summary
./scripts/project-cli.sh sprint-summary

# Add a new task
./scripts/project-cli.sh add-task "Implement route optimization"

# Mark issue as blocked
./scripts/project-cli.sh block 123 456

# Calculate velocity
./scripts/project-cli.sh velocity
```