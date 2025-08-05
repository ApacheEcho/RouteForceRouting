(build_tasks/auto_todo.md)
- [ ] Build route scoring integration into main route pipeline
- [ ] Add user-facing score breakdown UI
- [ ] Implement QA metrics and auto-correction logic
- [ ] Integrate summary logs into dashboard
- [ ] Finalize Playbook GUI injection logic
- [ ] Wire preflight QA checklist into route generation
- [ ] Improve routing traffic logic (Google Maps/OSRM)
- [ ] Add error notifications for broken routes

(scripts/autobuild.py)
import subprocess
import os

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

if __name__ == "__main__":
    run_copilot_autobuild()
