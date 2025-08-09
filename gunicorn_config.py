"""
Gunicorn configuration for RouteForce Routing Application
Production WSGI server configuration
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "eventlet"  # Required for Flask-SocketIO
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "routeforce-routing"

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None
user = None
group = None

# SSL (if needed)
keyfile = os.getenv("SSL_KEYFILE")
certfile = os.getenv("SSL_CERTFILE")

# Environment
raw_env = [
    f'FLASK_ENV={os.getenv("FLASK_ENV", "production")}',
    f'DATABASE_URL={os.getenv("DATABASE_URL", "")}',
    f'REDIS_URL={os.getenv("REDIS_URL", "")}',
]

# Performance tuning
preload_app = True
enable_stdio_inheritance = True
