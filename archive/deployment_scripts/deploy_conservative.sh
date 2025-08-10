#!/bin/bash
# Conservative Production Deployment Script for RouteForce

set -e  # Exit on any error

echo "🚀 Starting RouteForce Production Deployment (Conservative Mode)"

# Backup current deployment
echo "📦 Creating backup..."
if [ -d "backup_deployment" ]; then
    rm -rf "backup_deployment_old"
    mv "backup_deployment" "backup_deployment_old"
fi
mkdir -p backup_deployment
cp -r app/ backup_deployment/ 2>/dev/null || true
cp *.py backup_deployment/ 2>/dev/null || true

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies conservatively
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Validate configuration
echo "🔍 Validating configuration..."
python -c "
from app import create_app
try:
    app = create_app('production')
    print('✅ Production configuration valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

# Test database connection
echo "🗄️ Testing database connection..."
python -c "
try:
    from app.models.database import db
    from app import create_app
    app = create_app('production')
    with app.app_context():
        db.create_all()
    print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️ Database warning: {e}')
    print('Note: This is expected if database is not configured yet')
"

# Build frontend (if exists)
echo "🎨 Building frontend..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        npm run build
        echo "✅ Frontend built successfully"
    fi
    cd ..
else
    echo "ℹ️ No frontend directory found, skipping build"
fi

# Test application startup
echo "🧪 Testing application startup..."
timeout 10s python app.py &
APP_PID=$!
sleep 5

if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ Application starts successfully"
    kill $APP_PID
else
    echo "❌ Application failed to start"
    exit 1
fi

echo "🎉 Conservative deployment preparation complete!"
echo ""
echo "📋 Next steps for production deployment:"
echo "1. Update .env.production.template with your actual values"
echo "2. Copy to .env.production: cp .env.production.template .env.production"
echo "3. Configure your production database"
echo "4. Set up Redis (optional, will fallback to in-memory cache)"
echo "5. Deploy to your preferred hosting platform"
echo ""
echo "🔧 To run in production mode:"
echo "export FLASK_ENV=production && python app.py"
