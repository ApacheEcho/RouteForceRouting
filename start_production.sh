#!/bin/bash
# Production startup script for Render deployment
# Handles git availability gracefully and starts the application

echo "🚀 Starting RouteForce Production Deployment..."

# Environment setup
export FLASK_ENV=production
export AUTO_COMMIT_ENABLED=false
export GIT_AUTO_BACKUP=false

# Check if git is available (not required for production)
if command -v git &> /dev/null; then
    echo "✅ Git is available"
    git --version
else
    echo "⚠️  Git not found - auto-commit features will be disabled"
fi

# Check Python version
echo "🐍 Python version: $(python --version)"

# Verify required environment variables
echo "🔧 Environment check:"
echo "   PORT: ${PORT:-5000}"
echo "   FLASK_ENV: ${FLASK_ENV}"
echo "   AUTO_COMMIT_ENABLED: ${AUTO_COMMIT_ENABLED}"
echo "   DATABASE_URL: ${DATABASE_URL:0:30}..." # Only show first 30 chars for security
echo "   REDIS_URL: ${REDIS_URL:0:30}..."       # Only show first 30 chars for security

# Verify Python can import our modules
echo "🔍 Testing Python imports..."
python -c "from app import create_app; print('✅ App import successful')" || {
    echo "❌ Failed to import app"
    exit 1
}

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application with gunicorn
echo "🚀 Starting gunicorn server..."
echo "   Command: gunicorn --config gunicorn_config.py wsgi:app"
exec gunicorn --config gunicorn_config.py wsgi:app
