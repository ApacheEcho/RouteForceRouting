import os


def cleanup_after_task():
    try:
        os.remove("copilot_prompt.py")
        print("🧹 Cleanup complete: Removed copilot_prompt.py")
    except FileNotFoundError:
        pass


# Call after commit + push:
cleanup_after_task()
