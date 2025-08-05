#!/bin/bash

# RouteForce Routing - Codespaces Post-Create Setup
echo "🚀 Setting up RouteForce Routing development environment..."

# Ensure we're in the right directory
cd /workspaces/RouteForceRouting

# Upgrade pip to latest version
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating application directories..."
mkdir -p uploads
mkdir -p instance
mkdir -p logs

# Set up git configuration if not already set
echo "🔧 Configuring git..."
git config --global --add safe.directory /workspaces/RouteForceRouting

# Create a sample .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating sample .env file..."
    cat > .env << 'EOF'
# RouteForce Routing Environment Variables
# Copy this file and add your actual API keys

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Google Maps API (Required for geocoding)
# Get your API key from: https://developers.google.com/maps/documentation/javascript/get-api-key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GOOGLE_MAPS_API_SECRET=your_google_maps_api_secret_here

# Database Configuration (Optional for development)
# DATABASE_URL=postgresql://user:pass@localhost/routeforce

# Redis Configuration (Optional for development)
# CACHE_TYPE=redis
# CACHE_REDIS_URL=redis://localhost:6379
# RATELIMIT_STORAGE_URL=redis://localhost:6379

# Development Settings
PORT=8000
EOF
    echo "📝 Sample .env file created. Edit it with your actual API keys."
fi

# Run a quick test to ensure everything is working
echo "🧪 Testing Flask application import..."
if python -c "from app import create_app; print('✅ Flask app import successful')"; then
    echo "✅ Environment setup complete!"
else
    echo "❌ There was an issue with the setup. Check the logs above."
    exit 1
fi

echo ""
echo "🎉 RouteForce Routing development environment is ready!"
echo ""
echo "📋 Quick Start:"
echo "  1. Edit .env file with your Google Maps API key"
echo "  2. Run the development server: python app.py"
echo "  3. Access the app at: http://localhost:8000"
echo ""
echo "🧪 Run tests with: python -m pytest"
echo "🎨 Format code with: black ."
echo "🔍 Lint code with: flake8 ."
echo ""