#!/bin/bash

# RouteForce Routing Development Environment Setup Script
echo "🚀 Setting up RouteForce Routing development environment..."

# Set up Python environment
echo "🐍 Configuring Python environment..."
export PYTHONPATH="/app:$PYTHONPATH"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating example .env file..."
    cat > .env << EOF
# Google Maps API Configuration
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GOOGLE_MAPS_API_SECRET=your_google_maps_api_secret_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration (for development)
DATABASE_URL=sqlite:///routeforce.db

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0
EOF
    echo "⚠️  Please update .env with your actual API keys"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads logs .cache instance

# Set up pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🔧 Setting up pre-commit hooks..."
    pre-commit install || echo "⚠️  Pre-commit hooks not set up (optional)"
fi

# Run initial tests to verify setup
echo "🧪 Running initial tests..."
python -m pytest tests/ -x --tb=short || echo "⚠️  Some tests failed - this may be expected"

# Check code formatting
echo "🎨 Checking code formatting..."
python -m black --check . || echo "ℹ️  Run 'black .' to format code"

# Display helpful information
echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📋 Quick Start Commands:"
echo "  Start the app:     python app.py"
echo "  Run tests:         python -m pytest"
echo "  Format code:       python -m black ."
echo "  Lint code:         python -m flake8 ."
echo "  Install deps:      pip install -r requirements.txt"
echo ""
echo "🌐 The app will be available at:"
echo "  http://localhost:5000 (primary)"
echo "  http://localhost:8000 (alternative)"
echo ""
echo "💡 Don't forget to:"
echo "  1. Update .env with your Google Maps API key"
echo "  2. Review the README.md for detailed instructions"
echo ""