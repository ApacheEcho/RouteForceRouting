#!/usr/bin/env python
"""Import tasks from CSV and create GitHub issues."""

import os
import sys
import pandas as pd
from github import Github
from datetime import datetime


def import_issues():
    # Initialize GitHub client
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not found")
        sys.exit(1)

    g = Github(token)
    repo = g.get_repo(os.environ["GITHUB_REPOSITORY"])

    # Find CSV files
    csv_files = []
    if os.path.exists("routeforce_tasks.csv"):
        csv_files.append("routeforce_tasks.csv")
    if os.path.exists("imports"):
        csv_files.extend(
            [f"imports/{f}" for f in os.listdir("imports") if f.endswith(".csv")]
        )

    if not csv_files:
        print("No CSV files found to import")
        return

    for csv_file in csv_files:
        print(f"\nProcessing {csv_file}...")

        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            print(f"Found {len(df)} rows")

            # Create issues
            created_count = 0
            for _, row in df.iterrows():
                # Check if issue already exists
                title = f"[Task] {row.get('task_name', row.get('name', 'Unnamed'))}"

                existing = repo.get_issues(state="all", labels=["imported"])
                if any(title in issue.title for issue in existing):
                    print(f"Skipping duplicate: {title}")
                    continue

                # Determine priority and labels
                priority = row.get("priority", "medium").lower()
                labels = ["imported", "task", priority]

                if row.get("type"):
                    labels.append(row.get("type"))

                # Create issue body
                body = f"""
## Task Details
- **Store**: {row.get('store_name', row.get('store', 'N/A'))}
- **Priority**: {priority}
- **Due Date**: {row.get('due_date', 'N/A')}
- **Assigned Rep**: {row.get('rep_name', row.get('assigned_to', 'unassigned'))}
- **Route**: {row.get('route_id', 'N/A')}

## Description
{row.get('description', row.get('notes', 'No description provided'))}

## Additional Info
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC
- **Source**: {csv_file}
- **Row**: {_ + 2} (including header)

---
*Auto-imported by GitHub Action*
                """

                # Create issue
                issue = repo.create_issue(title=title, body=body.strip(), labels=labels)
                print(f"Created issue #{issue.number}: {issue.title}")
                created_count += 1

        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")
            continue

        print(f"Created {created_count} issues from {csv_file}")


if __name__ == "__main__":
    import_issues()
