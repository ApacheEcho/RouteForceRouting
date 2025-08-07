#!/bin/bash

# Post Start Command - Runs every time the container starts
set -e

echo "🚀 Starting RouteForceRouting services..."

# Start Redis if not running
if ! redis-cli -h redis ping > /dev/null 2>&1; then
    echo "⏳ Waiting for Redis to start..."
    sleep 5
fi

# Check PostgreSQL connection
if ! pg_isready -h postgres -p 5432 -U routeforce > /dev/null 2>&1; then
    echo "⏳ Waiting for PostgreSQL to start..."
    sleep 5
fi

# Set up log directories
mkdir -p /workspace/logs
touch /workspace/logs/app.log
touch /workspace/logs/error.log

# Display status
echo ""
echo "✅ Development environment is ready!"
echo ""
echo "🔗 Service Status:"

# Check services
if pg_isready -h postgres -p 5432 -U routeforce > /dev/null 2>&1; then
    echo "  ✅ PostgreSQL: Ready"
else
    echo "  ❌ PostgreSQL: Not Ready"
fi

if redis-cli -h redis ping > /dev/null 2>&1; then
    echo "  ✅ Redis: Ready"
else
    echo "  ❌ Redis: Not Ready"
fi

echo ""
echo "🚀 Ready to start development!"
echo "   Run 'rf-run' to start the Flask server"
echo ""
