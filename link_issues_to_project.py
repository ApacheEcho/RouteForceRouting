from github import Github
import os

# Load GitHub Token from environment only (do not hardcode tokens)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise SystemExit("❌ GITHUB_TOKEN not set. Export it securely or use GitHub Actions secrets.")

REPO_NAME = "ApacheEcho/RouteForceRouting"
PROJECT_NAME = "Route Force Pro"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Locate Project
projects = repo.get_projects()
project = next((p for p in projects if p.name == PROJECT_NAME), None)
if not project:
    print(f"❌ Project '{PROJECT_NAME}' not found.")
    exit(1)

# Map Issues/PRs to Project Cards
print(f"🔄 Linking open issues and PRs to project: {PROJECT_NAME}")
items = repo.get_issues(state="open")

for item in items:
    # Only link items not already in the project
    project_cards = [c.content_url for c in project.get_columns()[0].get_cards()]
    if item.url not in project_cards:
        project.get_columns()[0].create_card(content_id=item.id, content_type="Issue")
        print(f"✅ Linked: {item.title}")
    else:
        print(f"↪️ Already linked: {item.title}")