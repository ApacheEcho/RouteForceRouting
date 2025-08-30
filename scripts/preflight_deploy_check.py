#!/usr/bin/env python3
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]

def check(path: Path):
    ok = path.exists()
    print(f"{'✅' if ok else '❌'} {path}")
    return ok

def main():
    ok = True
    ok &= check(ROOT / "nginx/routeforce.conf")
    ok &= check(ROOT / "scripts/production_setup.sh")
    ok &= check(ROOT / "scripts/run_db_upgrade.sh")
    ok &= check(ROOT / "scripts/smoke_post_deploy.sh")
    ok &= check(ROOT / ".github/workflows/deploy.yml")
    ok &= check(ROOT / ".env.production.template")
    # Secrets in template
    text = (ROOT / ".env.production.template").read_text()
    for k in ["SECRET_KEY=", "JWT_SECRET_KEY=", "CORS_ORIGINS=", "METRICS_TOKEN="]:
        print(f"{'✅' if k in text else '❌'} template contains {k}")
        ok &= k in text
    print("✅ Ready" if ok else "❌ Missing items")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())

