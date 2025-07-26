import subprocess
import os
import re

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

def run_copilot_autobuild():
    extract_and_append_new_tasks()
    task = get_next_task()
    if not task:
        print("✅ All tasks completed.")
        return

    print(f"🔧 Running Copilot on task: {task}")

    # Prompt Copilot indirectly by opening the file with an embedded comment prompt
    prompt = f'# TASK: {task}\n# Please generate complete code for this task.\n'
    with open("copilot_prompt.py", "w") as f:
        f.write(prompt)

    subprocess.run(["code", "copilot_prompt.py"])
    print("✅ Auto-confirm enabled. Proceeding with commit and push...")

    os.system(f'git add . && git commit -m "Auto: {task}" && git push')

    mark_task_done(task)
    run_copilot_autobuild()

def extract_and_append_new_tasks():
    if not os.path.exists("copilot_prompt.py"):
        return
    with open("copilot_prompt.py", "r") as f:
        content = f.read()
    new_tasks = re.findall(r"- \[ \] .+", content)
    if new_tasks:
        with open(TODO_PATH, "a") as f:
            for task in new_tasks:
                f.write(f"{task}\n")
        print(f"🧠 Copilot suggested {len(new_tasks)} new task(s), added to todo list.")

if __name__ == "__main__":
    run_copilot_autobuild()
