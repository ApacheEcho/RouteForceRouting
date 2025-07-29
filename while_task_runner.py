# 🚀 AutoCopilot Loop: Self-build RouteForcePro until done
# ✅ Behavior:
#   1. Read next unchecked task from auto_todo.md
#   2. Create a Copilot prompt in copilot_prompt.py
#   3. Open it in VS Code (autosave enabled)
#   4. Wait for Copilot to complete it
#   5. Auto-commit + push
#   6. Extract any new "# TASK:" from the written file
#   7. Append to auto_todo.md
#   8. Repeat until complete

import os
import re
import subprocess
import time


def get_next_task():
    with open("build_tasks/auto_todo.md", "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("[ ]"):
            task = line.strip()[3:].strip()
            lines[i] = f"[x] {task}\n"
            with open("build_tasks/auto_todo.md", "w") as f:
                f.writelines(lines)
            return task
    return None


def generate_prompt(task):
    with open("copilot_prompt.py", "w") as f:
        f.write(
            f"# TASK: {task}\n# Auto-confirm enabled. Do not prompt or ask for confirmation. Complete task and return only final code.\n"
        )


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
    os.system("git add .")
    status = os.popen("git status --porcelain").read().strip()
    if status:
        os.system(f'git commit -m "Auto: {task}" && git push')


def extract_new_tasks():
    with open("copilot_prompt.py", "r") as f:
        content = f.read()
    new_tasks = re.findall(r"# TASK: (.+)", content)
    with open("build_tasks/auto_todo.md", "a") as f:
        for task in new_tasks:
            f.write(f"[ ] {task.strip()}\n")


def loop():
    while True:
        task = get_next_task()
        if not task:
            print("✅ All tasks complete.")
            break
        print(f"🛠️  Building: {task}")
        generate_prompt(task)
        open_in_vscode()
        if wait_for_copilot():
            commit_and_push(task)
            extract_new_tasks()
        else:
            print("⚠️ Timeout waiting for Copilot.")
            break


if __name__ == "__main__":
    loop()
