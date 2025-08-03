#!/usr/bin/env python3
"""
import_issues.py
===================

This script reads a CSV file describing GitHub issues and creates those
issues via the GitHub REST API. It is intended to be run in the context of
a GitHub Actions workflow triggered when a file named `routeforce_tasks.csv`
is added or modified in the repository root.

The CSV must have the following column headers (case‑insensitive):

* **title** (required) – the issue title
* **body** (required) – the issue body/description
* **labels** (required) – a comma‑separated list of labels
* **assignee** (optional) – the username to assign the issue to

Each row in the CSV results in a call to the GitHub API to create an issue
in the current repository. If an issue cannot be created, an error is
written to stdout and appended to `issue_failures.log`.

Environment variables used:
* `GITHUB_TOKEN` – token used to authenticate to the GitHub API. This is
  automatically provided in GitHub Actions as `secrets.GITHUB_TOKEN`.
* `GITHUB_REPOSITORY` – the "owner/repo" identifier. In GitHub Actions
  this is available by default. If absent, the script fails.
* `CSV_FILE` – path to the CSV file. Defaults to `routeforce_tasks.csv`.

The script validates that the CSV contains the required headers and skips
rows that lack required fields.

"""

import csv
import json
import logging
import os
import sys
from typing import List, Dict

try:
    import requests  # type: ignore
except ImportError as exc:
    print("The 'requests' library is required. Please install it with pip install requests.", file=sys.stderr)
    raise


def read_csv(path: str) -> List[Dict[str, str]]:
    """Read the CSV file and return a list of dictionaries representing rows.

    The CSV must contain at least the columns: title, body, labels. Column
    names are treated case‑insensitively. Extra columns are ignored except
    `assignee` which is optional. Values are stripped of surrounding
    whitespace.

    :param path: Path to the CSV file.
    :raises FileNotFoundError: if the file is not present.
    :raises ValueError: if required headers are missing.
    :return: A list of dictionaries keyed by lowercased column names.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"CSV file not found: {path}")

    with open(path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file appears to be empty or malformed (no headers)")
        # Normalize field names to lower case for easier lookup
        field_map = {name.lower(): name for name in reader.fieldnames}
        required_fields = {"title", "body", "labels"}
        missing = required_fields - set(field_map.keys())
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        optional_fields = {"assignee"}

        rows = []
        for raw_row in reader:
            # Create a row with lower‑cased keys and strip whitespace
            row: Dict[str, str] = {}
            for lc_name, orig_name in field_map.items():
                val = raw_row.get(orig_name, "")
                # skip if val is None; unify to empty string
                row[lc_name] = val.strip() if val is not None else ""
            # Filter to only required + optional columns
            filtered: Dict[str, str] = {k: row[k] for k in required_fields.union(optional_fields) if k in row}
            rows.append(filtered)
        return rows


class GitHubIssueImporter:
    """Helper class to create GitHub issues from CSV rows."""

    def __init__(self, token: str, repository: str) -> None:
        self.token = token.strip()
        self.repository = repository.strip()
        self.base_url = f"https://api.github.com/repos/{self.repository}"
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        self.logger = logging.getLogger(__name__)
        self.failure_log_path = "issue_failures.log"

    def _post(self, endpoint: str, payload: Dict) -> requests.Response:
        """Make an authenticated POST request to the GitHub API."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response

    def create_issue(self, row: Dict[str, str]) -> None:
        """Create a single issue from a CSV row.

        :param row: A dictionary with keys: title, body, labels, and optional assignee.
        """
        title = row.get("title", "").strip()
        body = row.get("body", "").strip()
        labels_raw = row.get("labels", "").strip()
        assignee = row.get("assignee", "").strip()

        if not title:
            self._log_failure(row, "Missing title; issue not created.")
            return
        if not body:
            self._log_failure(row, "Missing body; issue not created.")
            return
        if not labels_raw:
            self._log_failure(row, "Missing labels; issue not created.")
            return

        labels: List[str] = [lbl.strip() for lbl in labels_raw.split(",") if lbl.strip()]
        payload: Dict[str, any] = {
            "title": title,
            "body": body,
            "labels": labels,
        }
        if assignee:
            payload["assignees"] = [assignee]

        self.logger.info(f"Creating issue: {title}")
        resp = self._post("/issues", payload)
        if resp.status_code == 201:
            self.logger.info(f"✅ Issue created: {title}")
        else:
            err_detail = ""
            try:
                data = resp.json()
                err_detail = data.get("message", "")
            except Exception:
                err_detail = resp.text
            msg = f"Failed to create issue '{title}'. HTTP {resp.status_code}: {err_detail}"
            self._log_failure(row, msg)

    def _log_failure(self, row: Dict[str, str], message: str) -> None:
        """Log a failure to both stdout and a failure log file."""
        log_entry = f"[ERROR] {message} | Row: {json.dumps(row, ensure_ascii=False)}"
        self.logger.error(log_entry)
        # Append to failure log file
        try:
            with open(self.failure_log_path, mode="a", encoding="utf-8") as fout:
                fout.write(log_entry + "\n")
        except Exception as exc:
            self.logger.error(f"Unable to write to failure log: {exc}")


def main() -> int:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN is not set; cannot authenticate to GitHub API.", file=sys.stderr)
        return 1
    repository = os.getenv("GITHUB_REPOSITORY")
    if not repository:
        print("GITHUB_REPOSITORY is not set; cannot determine repository.", file=sys.stderr)
        return 1
    csv_file = os.getenv("CSV_FILE", "routeforce_tasks.csv")
    try:
        rows = read_csv(csv_file)
    except Exception as exc:
        print(f"Error reading CSV file '{csv_file}': {exc}", file=sys.stderr)
        return 1

    importer = GitHubIssueImporter(token=token, repository=repository)
    any_failures = False
    for row in rows:
        # Create issues sequentially
        try:
            importer.create_issue(row)
        except Exception as exc:
            any_failures = True
            importer._log_failure(row, f"Unexpected exception: {exc}")
    if any_failures:
        print("One or more issues failed to create. See issue_failures.log for details.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())