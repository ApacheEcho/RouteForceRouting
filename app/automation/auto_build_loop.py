"""
Auto Build Loop for RouteForceRouting
Continuously watches for file changes and triggers build/test/deploy steps.
"""

import os
import subprocess
import time
from pathlib import Path

WATCH_PATHS = [
    Path(__file__).parent.parent,  # Watch the app/ directory
]
EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache", "venv", ".mypy_cache"}
POLL_INTERVAL = 2  # seconds


def get_all_files(paths):
    files = set()
    for path in paths:
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for filename in filenames:
                if filename.endswith(".py"):
                    files.add(os.path.join(root, filename))
    return files


def get_mtime_map(files):
    return {f: os.path.getmtime(f) for f in files}


def run_build():
    print("[auto_build_loop] Running: pytest -v")
    result = subprocess.run(["pytest", "-v"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("[auto_build_loop] Tests failed!")
    else:
        print("[auto_build_loop] All tests passed.")


def main():
    print("[auto_build_loop] Starting auto build loop...")
    files = get_all_files(WATCH_PATHS)
    mtime_map = get_mtime_map(files)
    while True:
        time.sleep(POLL_INTERVAL)
        new_files = get_all_files(WATCH_PATHS)
        new_mtime_map = get_mtime_map(new_files)
        if new_mtime_map != mtime_map:
            print("[auto_build_loop] Change detected. Running build/tests...")
            run_build()
            mtime_map = new_mtime_map


if __name__ == "__main__":
    main()
