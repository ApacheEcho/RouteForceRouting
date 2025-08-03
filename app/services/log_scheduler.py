import os
import time
import logging
import schedule
import subprocess

def run_exporter():
    cmd = ["python3", "-m", "app.services.log_exporter"]
    if os.getenv("LOG_EXPORT_DRY_RUN", "false").lower() == "true":
        cmd.append("--dry-run")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        logging.info(result.stdout)
        if result.stderr:
            logging.error(result.stderr)
    except Exception as e:
        logging.error(f"Log exporter failed: {e}")

def main():
    logging.basicConfig(filename="logs/log_export_scheduler.log", level=logging.INFO)
    if os.getenv("LOG_EXPORT_SCHEDULE_ENABLED", "true").lower() != "true":
        print("Log export scheduler is disabled by .env")
        return
    interval = int(os.getenv("LOG_EXPORT_SCHEDULE_INTERVAL", "60"))
    schedule.every(interval).minutes.do(run_exporter)
    print(f"Log export scheduler started. Interval: {interval} minutes.")
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    main()
