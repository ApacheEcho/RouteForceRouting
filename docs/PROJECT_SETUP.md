# RouteForce GitHub Project Setup Guide

## ✅ Automated Project Configuration

This repository includes comprehensive project board automation that works out of the box. The automation includes:

### 🤖 GitHub Actions Workflows

1. **Basic Project Automation** (`.github/workflows/project-automation.yml`)
   - Auto-labels new issues as "needs-triage"
   - Marks closed issues as "completed"
   - Processes both issues and pull requests

2. **Advanced Project Automation** (`.github/workflows/advanced-project-automation.yml`)
   - Auto-assigns based on component labels
   - Detects blocking relationships
   - Auto-prioritizes based on keywords (critical, urgent)
   - Categorizes bugs, features, and automation tasks
   - Adds appropriate labels automatically

### 📋 Custom Fields Configuration

Run the setup script to see recommended project fields:
```bash
node scripts/setup-project-fields.js
```

Recommended custom fields for your GitHub Project:

#### Story Points (Number)
- **Description**: Estimated effort (1, 2, 3, 5, 8, 13)
- **Usage**: For sprint planning and velocity tracking

#### Sprint (Single Select)
- **Options**: Sprint 1, Sprint 2, Sprint 3, Sprint 4, Backlog
- **Usage**: Track which sprint items belong to

#### Component (Single Select)
- **Options**: Backend, Frontend, API, Database, DevOps, Documentation
- **Usage**: Categorize work by system component

#### Priority (Single Select)
- **Options**: High, Medium, Low
- **Usage**: Automatically set based on title keywords

#### Due Date (Date)
- **Usage**: Track deadlines for deliverables

#### Blocked By (Text)
- **Description**: Issue numbers blocking this work
- **Usage**: Track dependencies between tasks

### ⚡ Automation Rules

The following automation rules are configured in the workflows:

1. **Auto-add new issues**
   - When: Item added to project
   - Then: Set Status to "Backlog", Add "needs-triage" label

2. **Move to In Progress**
   - When: Item labeled with "in-progress"
   - Then: Set Status to "In Progress"

3. **Move to Done**
   - When: Item closed
   - Then: Set Status to "Done", Add "completed" label

4. **Auto-prioritize**
   - When: Title contains "urgent" or "critical"
   - Then: Set Priority to "High", Add "high-priority" label

5. **Bug Detection**
   - When: Title contains "bug" or "fix"
   - Then: Add "bug" and "needs-investigation" labels

6. **Feature Detection**
   - When: Title contains "feature" or "enhancement"
   - Then: Add "enhancement" and "feature-request" labels

7. **Automation Tasks**
   - When: Title contains "automation", "setup", or "configure"
   - Then: Add "automation" and "configuration" labels

### 🔧 Setup Instructions

1. **Create/Access Project Board**
   - Go to your repository → Projects tab
   - Create new project or select existing one
   - Use "Table" or "Board" view as preferred

2. **Configure Custom Fields** (Manual - one time setup)
   - In project settings → Custom fields
   - Add the fields listed above with their respective types and options

3. **Enable Automation** (Already configured via workflows)
   - The GitHub Actions workflows handle automation automatically
   - No additional setup required for basic functionality

4. **Optional: Set Project URL Variable**
   - In repository Settings → Secrets and variables → Actions
   - Add variable `PROJECT_URL` with your project URL
   - Format: `https://github.com/users/USERNAME/projects/NUMBER`

### 🎯 Using the Project CLI

The repository includes a CLI tool for common project operations:

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

### 📊 Project Views

The automation supports these recommended project views:

1. **Sprint Board** (Board layout)
   - Columns: Backlog, In Progress, Review, Done
   - Filtered by status and labels

2. **Priority View** (Table layout)
   - Grouped by priority
   - Shows title, assignees, labels, milestone
   - Sorted by priority (High → Low)

### 🔄 Continuous Improvement

The automation rules can be extended by:
1. Modifying the GitHub Actions workflows in `.github/workflows/`
2. Adding new label-based triggers
3. Integrating with external tools via webhooks
4. Expanding the project CLI functionality

### 📈 Monitoring

Track automation effectiveness through:
- Issue velocity and burn-down charts
- Label distribution analytics
- Time-to-resolution metrics
- Project field completion rates