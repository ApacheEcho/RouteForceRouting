#!/usr/bin/env python3
"""
Preflight checks for RouteForce production deployment.

Validates presence of critical files, configuration templates, and CI/CD variables
referenced by the workflow. Prints a concise summary with pass/fail markers.
"""

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check_file(path: Path, desc: str) -> bool:
    ok = path.exists()
    print(f"{'✅' if ok else '❌'} {desc}: {path}")
    return ok


def check_env_template_keys(template_path: Path, keys: list[str]) -> bool:
    ok = True
    text = template_path.read_text(encoding="utf-8") if template_path.exists() else ""
    for key in keys:
        present = f"{key}=" in text
        print(f"{'✅' if present else '❌'} .env.production.template contains {key}")
        ok = ok and present
    return ok


def check_workflow_vars(workflow_path: Path, vars_: list[str]) -> bool:
    ok = True
    text = workflow_path.read_text(encoding="utf-8") if workflow_path.exists() else ""
    for v in vars_:
        present = v in text
        print(f"{'✅' if present else '❌'} deploy.yml references {v}")
        ok = ok and present
    return ok


def main() -> int:
    print("🧪 RouteForce Deployment Preflight Checks\n==============================")

    all_ok = True

    # Critical files
    all_ok &= check_file(ROOT / "nginx/routeforce.conf", "NGINX config present")
    all_ok &= check_file(ROOT / "scripts/production_setup.sh", "Production setup script present")
    all_ok &= check_file(ROOT / "scripts/setup_postgresql.sh", "PostgreSQL setup helper present")
    all_ok &= check_file(ROOT / "scripts/setup_ssl.sh", "SSL setup helper present")
    all_ok &= check_file(ROOT / "scripts/routeforce.service", "Systemd service file present")
    all_ok &= check_file(ROOT / ".github/workflows/deploy.yml", "GitHub Actions deploy workflow present")
    all_ok &= check_file(ROOT / "Procfile", "Procfile present")
    all_ok &= check_file(ROOT / "wsgi.py", "WSGI entrypoint present")
    all_ok &= check_file(ROOT / "app.py", "App entrypoint present (factory)")

    # Environment template sanity
    template_ok = check_env_template_keys(
        ROOT / ".env.production.template",
        [
            "SECRET_KEY",
            "JWT_SECRET_KEY",
            "DATABASE_URL",
            "CORS_ORIGINS",
        ],
    )
    all_ok &= template_ok

    # Workflow secrets for Render deploy
    workflow_ok = check_workflow_vars(
        ROOT / ".github/workflows/deploy.yml",
        ["RENDER_DEPLOY_HOOK", "RENDER_API_KEY", "RENDER_SERVICE_ID"],
    )
    all_ok &= workflow_ok

    # Gunicorn entrypoint sanity
    proc_txt = (ROOT / "Procfile").read_text(encoding="utf-8") if (ROOT / "Procfile").exists() else ""
    gunicorn_refs_ok = "app:app" in proc_txt or "app:create_app" in proc_txt
    print(f"{'✅' if gunicorn_refs_ok else '❌'} Procfile points to a valid app entry")
    all_ok &= gunicorn_refs_ok

    print("\nResult:")
    if all_ok:
        print("✅ Preflight checks passed. Ready for deployment.")
        return 0
    else:
        print("❌ Preflight checks failed. See items above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

