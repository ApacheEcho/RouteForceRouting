#!/bin/bash
# RouteForce Routing Application Start Script
# Handles both development and production startup

set -e

# Set environment variables with defaults
export FLASK_ENV=${FLASK_ENV:-development}
export PORT=${PORT:-8000}
export PYTHONPATH=${PYTHONPATH:-$(pwd)}

echo "🚀 Starting RouteForce Routing Application"
echo "Environment: ${FLASK_ENV}"
echo "Port: ${PORT}"

# Install dependencies if needed
if [ ! -f ".dependencies_installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch .dependencies_installed
fi

# Check if we're in production environment
if [ "$FLASK_ENV" = "production" ] || [ -n "$RENDER" ] || [ -n "$HEROKU" ]; then
    echo "🏭 Production mode: Starting with Gunicorn"
    exec gunicorn --config gunicorn_config.py app:app
else
    echo "🔧 Development mode: Starting with Flask dev server"
    exec python app.py
fi
