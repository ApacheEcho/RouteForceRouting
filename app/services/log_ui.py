import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from app.services import log_preview, log_filters
from datetime import datetime
import io
import csv
import json

app = Flask(__name__)
app.secret_key = os.getenv('LOG_UI_SECRET_KEY', 'change-this-key')
UI_ENABLED = os.getenv('LOG_UI_ENABLED', 'true').lower() == 'true'
UI_PASSWORD = os.getenv('LOG_UI_PASSWORD', 'admin')

@app.before_request
def check_enabled():
    if not UI_ENABLED and request.endpoint != 'static':
        return "Log UI is disabled.", 403

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == UI_PASSWORD:
            session['auth'] = True
            return redirect(url_for('logs'))
        flash('Invalid password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('auth', None)
    return redirect(url_for('login'))

@app.before_request
def require_auth():
    if request.endpoint not in ('login', 'static') and not session.get('auth'):
        return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/logs', methods=['GET', 'POST'])
def logs():
    log_path = os.getenv('AUDIT_LOG_PATH', 'logs/audit.log')
    logs = log_preview.load_logs(log_path)
    route_id = request.values.get('route_id')
    user_id = request.values.get('user_id')
    start = request.values.get('start')
    end = request.values.get('end')
    s_dt = datetime.fromisoformat(start) if start else None
    e_dt = datetime.fromisoformat(end) if end else None
    filtered = log_filters.apply_filters(logs, route_id, user_id, s_dt, e_dt)
    page = int(request.values.get('page', 1))
    per_page = 20
    total = len(filtered)
    paged = filtered[(page-1)*per_page:page*per_page]
    return render_template('logs.html', logs=paged, page=page, total=total, per_page=per_page, route_id=route_id, user_id=user_id, start=start, end=end)

@app.route('/export')
def export():
    log_path = os.getenv('AUDIT_LOG_PATH', 'logs/audit.log')
    logs = log_preview.load_logs(log_path)
    route_id = request.values.get('route_id')
    user_id = request.values.get('user_id')
    start = request.values.get('start')
    end = request.values.get('end')
    s_dt = datetime.fromisoformat(start) if start else None
    e_dt = datetime.fromisoformat(end) if end else None
    filtered = log_filters.apply_filters(logs, route_id, user_id, s_dt, e_dt)
    fmt = request.values.get('format', 'json')
    if fmt == 'csv':
        si = io.StringIO()
        if filtered:
            writer = csv.DictWriter(si, fieldnames=filtered[0].keys())
            writer.writeheader()
            for row in filtered:
                writer.writerow(row)
        output = io.BytesIO(si.getvalue().encode())
        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='logs.csv')
    else:
        output = io.BytesIO(json.dumps(filtered, indent=2).encode())
        return send_file(output, mimetype='application/json', as_attachment=True, download_name='logs.json')

if __name__ == '__main__':
    app.run(debug=True)
