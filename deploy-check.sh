#!/bin/bash
# RouteForce Routing - Production Deployment Helper
# Quick diagnostics and deployment commands

set -e

echo "🔍 RouteForce Routing Deployment Diagnostics"
echo "=============================================="

# Check Python version
echo "Python Version:"
python3 --version || echo "❌ Python3 not found"

# Check if Gunicorn is installed
echo -e "\nGunicorn Status:"
pip show gunicorn 2>/dev/null && echo "✅ Gunicorn installed" || echo "❌ Gunicorn not installed"

# Check if eventlet is installed (needed for SocketIO)
echo -e "\nEventlet Status:"
pip show eventlet 2>/dev/null && echo "✅ Eventlet installed" || echo "❌ Eventlet not installed"

# Test app import
echo -e "\nApp Import Test:"
python3 -c "from app import create_app; print('✅ App imports successfully')" 2>/dev/null || echo "❌ App import failed"

# Test Gunicorn config
echo -e "\nGunicorn Config Test:"
if [ -f "gunicorn_config.py" ]; then
    echo "✅ Gunicorn config found"
    python3 -c "import gunicorn_config; print('✅ Gunicorn config valid')" 2>/dev/null || echo "❌ Gunicorn config invalid"
else
    echo "❌ Gunicorn config not found"
fi

# Environment check
echo -e "\nEnvironment Variables:"
echo "FLASK_ENV: ${FLASK_ENV:-not set}"
echo "PORT: ${PORT:-not set}"
echo "RENDER: ${RENDER:-not set}"
echo "DATABASE_URL: ${DATABASE_URL:+set (hidden)}"
echo "REDIS_URL: ${REDIS_URL:+set (hidden)}"

# Health check endpoint test (if app is running)
echo -e "\nHealth Check:"
if curl -f http://localhost:${PORT:-8000}/health -m 5 2>/dev/null; then
    echo "✅ Health endpoint accessible"
else
    echo "❌ Health endpoint not accessible (app may not be running)"
fi

echo -e "\n🚀 Quick Start Commands:"
echo "Development: ./start.sh"
echo "Production:  gunicorn --config gunicorn_config.py app:app"
echo "Docker:      docker build -f Dockerfile.production -t routeforce ."
echo "Test Import: python3 -c 'from app import create_app; app = create_app(); print(\"App created successfully\")'"

echo -e "\n📝 Recent Deployment Notes:"
echo "- Fixed Werkzeug production error"
echo "- Added Gunicorn with eventlet worker for SocketIO"
echo "- Updated Render configuration"
echo "- Added proper production startup commands"
