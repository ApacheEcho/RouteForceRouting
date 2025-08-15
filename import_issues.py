import csv
import os
import requests

# Load from GitHub Action secrets
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]
CSV_FILE = "routeforce_epic_tasks.csv"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def create_issue(title, body, labels, assignees):
    url = f"https://api.github.com/repos/{REPO}/issues"
    data = {
        "title": title,
        "body": body,
        "labels": [l.strip() for l in labels.split(",") if l.strip()],
        "assignees": [a.strip() for a in assignees.split(",") if a.strip()],
    }
    r = requests.post(url, headers=headers, json=data)
    print(f"{title}: {r.status_code} - {r.json().get('html_url')}")


def run():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            create_issue(
                row["title"], row["body"], row["labels"], row["assignees"]
            )


if __name__ == "__main__":
    run()
