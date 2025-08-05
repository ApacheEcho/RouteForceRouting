# Scripts Directory

This directory contains utility scripts for the RouteForceRouting project.

## Label Standardization

### `standardize_labels.py`

A comprehensive GitHub label management script that applies the standardized label system defined in `.github/labels.yml`.

**Features:**
- Creates and updates GitHub repository labels
- Removes legacy labels
- Validates label configuration
- Provides detailed logging and statistics

**Usage:**
```bash
# Apply label standardization
python scripts/standardize_labels.py

# Validate labels only (no changes)
python scripts/standardize_labels.py --validate-only
```

**Requirements:**
- PyGithub: `pip install PyGithub`
- PyYAML: `pip install PyYAML`
- GITHUB_TOKEN environment variable with repo access

**Environment Variables:**
- `GITHUB_TOKEN`: GitHub personal access token with repository permissions
- `GITHUB_REPOSITORY`: Repository name in format "owner/repo" (optional, defaults to ApacheEcho/RouteForceRouting)

**Configuration:**
Labels are defined in `.github/labels.yml` with the following structure:
- Priority labels: `priority:critical`, `priority:high`, `priority:medium`, `priority:low`
- Type labels: `type:bug`, `type:feature`, `type:enhancement`, etc.
- Status labels: `status:triage`, `status:in-progress`, `status:review`, etc.
- Component labels: `component:backend`, `component:frontend`, `component:mobile`, etc.

See `.github/LABELS.md` for complete documentation of the label system.