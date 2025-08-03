import os
import requests
import re

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")
LABELS_FILE = "labels.md"
API_URL = f"https://api.github.com/repos/{REPO}/labels"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def parse_labels(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    labels = []
    for line in lines:
        if line.strip().startswith("|") and not line.startswith("| Label"):
            parts = [part.strip() for part in line.strip().split("|")[1:-1]]
            if len(parts) == 3:
                label = {
                    "name": parts[0],
                    "color": parts[1].lstrip("#"),
                    "description": parts[2]
                }
                labels.append(label)
    return labels

def get_existing_labels():
    resp = requests.get(API_URL, headers=HEADERS)
    resp.raise_for_status()
    return {label["name"]: label for label in resp.json()}

def sync_labels():
    labels = parse_labels(LABELS_FILE)
    existing = get_existing_labels()

    for label in labels:
        if label["name"] in existing:
            existing_label = existing[label["name"]]
            if (existing_label["color"].lower() != label["color"].lower()
                or existing_label["description"] != label["description"]):
                print(f"Updating: {label['name']}")
                requests.patch(f"{API_URL}/{label['name']}", headers=HEADERS, json=label)
        else:
            print(f"Creating: {label['name']}")
            requests.post(API_URL, headers=HEADERS, json=label)

if __name__ == "__main__":
    sync_labels()