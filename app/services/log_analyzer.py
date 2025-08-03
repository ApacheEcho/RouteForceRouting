import os
import click
import json
from datetime import datetime
from app.services import log_preview, log_filters

@click.group()
def cli():
    pass

@cli.command()
@click.option('--route-id', help='Filter by route_id')
@click.option('--user-id', help='Filter by user')
@click.option('--start', help='Start time (YYYY-MM-DD or ISO8601)')
@click.option('--end', help='End time (YYYY-MM-DD or ISO8601)')
@click.option('--export', type=click.Choice(['csv', 'json']), help='Export format')
@click.option('--log-path', default=None, help='Override log file path')
def view(route_id, user_id, start, end, export, log_path):
    log_path = log_path or os.getenv('AUDIT_LOG_PATH', 'logs/audit.log')
    logs = log_preview.load_logs(log_path)
    s_dt = datetime.fromisoformat(start) if start else None
    e_dt = datetime.fromisoformat(end) if end else None
    filtered = log_filters.apply_filters(logs, route_id, user_id, s_dt, e_dt)
    if export == 'json':
        print(json.dumps(filtered, indent=2))
    elif export == 'csv':
        import csv, sys
        if filtered:
            writer = csv.DictWriter(sys.stdout, fieldnames=filtered[0].keys())
            writer.writeheader()
            for row in filtered:
                writer.writerow(row)
    else:
        for log in filtered:
            print(json.dumps(log, indent=2))

@cli.command()
@click.option('--log-path', default=None, help='Override log file path')
def preview(log_path):
    log_path = log_path or os.getenv('AUDIT_LOG_PATH', 'logs/audit.log')
    logs = log_preview.load_logs(log_path)
    for log in logs[:10]:
        print(json.dumps(log, indent=2))

if __name__ == '__main__':
    cli()
