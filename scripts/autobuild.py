
import os
import re
import subprocess
import argparse
import sys
import time

TODO_PATH = "build_tasks/auto_todo.md"

def get_next_task():
    with open(TODO_PATH, "r") as f:
        for line in f:
            if line.startswith("- [ ]"):
                return line.strip().replace("- [ ] ", "")
    return None

def mark_task_done(task):
    with open(TODO_PATH, "r") as f:
        lines = f.readlines()
    with open(TODO_PATH, "w") as f:
        for line in lines:
            if task in line and "- [ ]" in line:
                f.write(line.replace("- [ ]", "- [x]"))
            else:
                f.write(line)

def generate_prompt(task, auto_confirm=True, mode="auto"):
    with open("copilot_prompt.py", "w") as f:
        f.write(f"# TASK: {task}\n")
        if auto_confirm:
            f.write("# Auto-confirm enabled. Do not prompt or ask for confirmation. Complete task and return only final code.\n")
        f.write(f"# X-Copilot-Mode: {mode}\n")

def open_in_vscode():
    subprocess.run(["code", "copilot_prompt.py"])

def wait_for_copilot(timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        with open("copilot_prompt.py", "r") as f:
            content = f.read()
            if "# TASK:" in content and "Please generate complete code" not in content:
                return True
        time.sleep(3)
    return False

def commit_and_push(task):
    os.system('git add .')
    status = os.popen('git status --porcelain').read().strip()
    if status:
        os.system(f'git commit -m "Auto: {task}" && git push')

def extract_and_append_new_tasks():
    if not os.path.exists("copilot_prompt.py"):
        return
    with open("copilot_prompt.py", "r") as f:
        content = f.read()
    # Accept both markdown and comment style tasks
    new_tasks = re.findall(r"- \[ \] .+|# TASK: (.+)", content)
    tasks_to_add = []
    for t in new_tasks:
        if isinstance(t, tuple):
            t = t[0]
        if t and not t.startswith("- [ ]"):
            tasks_to_add.append(f"- [ ] {t.strip()}")
        elif t:
            tasks_to_add.append(t.strip())
    if tasks_to_add:
        with open(TODO_PATH, "a") as f:
            for task in tasks_to_add:
                f.write(f"{task}\n")
        print(f"🧠 Copilot suggested {len(tasks_to_add)} new task(s), added to todo list.")

def cleanup_tmp_files():
    for fname in ["copilot_prompt.py"]:
        if os.path.exists(fname):
            os.remove(fname)

def notify_task_complete(task):
    # Placeholder for webhook or notification logic
    print(f"✅ Task complete: {task}")

def run_copilot_autobuild(args=None):
    extract_and_append_new_tasks()
    while True:
        task = get_next_task()
        if not task:
            print("✅ All tasks completed.")
            break
        print(f"🔧 Running Copilot on task: {task}")
        generate_prompt(task, auto_confirm=True, mode="auto")
        open_in_vscode()
        if args and getattr(args, "autosave", False):
            print("💾 Autosave enabled.")
        if args and getattr(args, "autoloop", False):
            print("🔁 Autoloop enabled.")
        if args and getattr(args, "notify", False):
            notify_task_complete(task)
        if wait_for_copilot():
            commit_and_push(task)
            extract_and_append_new_tasks()
        else:
            print("⚠️ Timeout waiting for Copilot.")
            break
        mark_task_done(task)
        if args and getattr(args, "cleanup", False):
            cleanup_tmp_files()

def main():
    parser = argparse.ArgumentParser(description="Autonomous Copilot Autobuild Script")
    parser.add_argument("--autoloop", action="store_true", help="Enable autoloop mode")
    parser.add_argument("--autosave", action="store_true", help="Enable autosave mode")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup temp files after each task")
    parser.add_argument("--notify", action="store_true", help="Notify on task completion")
    args = parser.parse_args()
    run_copilot_autobuild(args)

if __name__ == "__main__":
    main()
