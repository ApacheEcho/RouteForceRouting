#!/bin/bash

# Post Create Command - Runs after container is created
set -e

echo "🚀 Setting up RouteForceRouting development environment..."

# Update pip and install requirements
echo "📦 Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️ Pre-commit not found, skipping hooks installation"
fi

# Set up git configuration if not already configured
if [ -z "$(git config --global user.name)" ]; then
    echo "🔧 Configuring git..."
    git config --global user.name "Codespaces User"
    git config --global user.email "user@example.com"
    echo "⚠️ Please configure your git user.name and user.email"
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs temp backups static/uploads tests/fixtures

# Set up environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Development Environment Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=postgresql://routeforce:password@postgres:5432/routeforce_dev
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-dev-secret-key

# External APIs (add your keys here)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
SENTRY_DSN=your-sentry-dsn

# Performance
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://redis:6379/1

# Development Settings
LOG_LEVEL=DEBUG
TESTING=False
EOF
    echo "✅ .env file created"
fi

# Install frontend dependencies if package.json exists
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Run database setup (if needed)
echo "🗄️ Setting up database..."
# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432 -U routeforce; do
  echo "⏳ Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Initialize database if migrations exist
if [ -d "migrations" ]; then
    echo "🗄️ Running database migrations..."
    python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://routeforce:password@postgres:5432/routeforce_dev'
try:
    from flask import Flask
    from flask_migrate import upgrade
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
    with app.app_context():
        upgrade()
    print('✅ Database migrations completed')
except Exception as e:
    print(f'⚠️ Database migration failed: {e}')
    print('You may need to run: flask db init && flask db migrate && flask db upgrade')
"
fi

# Set correct permissions
echo "🔧 Setting permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x .devcontainer/*.sh

# Create helpful aliases
echo "🔧 Setting up development aliases..."
cat >> ~/.bashrc << 'EOF'

# RouteForceRouting Development Aliases
alias rf-run='python app.py'
alias rf-test='pytest -v'
alias rf-test-cov='pytest --cov=. --cov-report=html'
alias rf-lint='flake8 . && black --check . && isort --check-only .'
alias rf-format='black . && isort .'
alias rf-db-migrate='flask db migrate'
alias rf-db-upgrade='flask db upgrade'
alias rf-shell='python -c "from app import app; app.app_context().push(); import IPython; IPython.start_ipython()"'
alias rf-logs='tail -f logs/*.log'
alias rf-deps='pip install -r requirements.txt && pip install -r requirements-dev.txt'

# Docker aliases
alias dc='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dcbuild='docker-compose build'
alias dclogs='docker-compose logs -f'

# Git aliases
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git pull'
alias gco='git checkout'
alias gb='git branch'
alias gd='git diff'

EOF

echo ""
echo "🎉 RouteForceRouting development environment setup complete!"
echo ""
echo "📋 Quick Start Commands:"
echo "  rf-run        - Start the Flask development server"
echo "  rf-test       - Run the test suite"
echo "  rf-test-cov   - Run tests with coverage report"
echo "  rf-lint       - Check code quality"
echo "  rf-format     - Format code with black and isort"
echo "  rf-shell      - Open Flask shell with app context"
echo ""
echo "🐳 Docker Commands:"
echo "  dcup          - Start all services"
echo "  dcdown        - Stop all services"
echo "  dclogs        - View service logs"
echo ""
echo "🗄️ Database Commands:"
echo "  rf-db-migrate - Create new migration"
echo "  rf-db-upgrade - Apply migrations"
echo ""
echo "🌐 Available Services:"
echo "  - Flask App:    http://localhost:5000"
echo "  - PgAdmin:      http://localhost:8080 (admin@routeforce.local/admin)"
echo "  - PostgreSQL:   localhost:5432 (routeforce/password)"
echo "  - Redis:        localhost:6379"
echo ""
echo "⚠️  Don't forget to configure your .env file with actual API keys!"
echo ""
