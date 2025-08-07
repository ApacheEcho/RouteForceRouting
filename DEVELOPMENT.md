# RouteForce Routing - Development Guide

## 🚀 Quick Start

### Initial Setup (First Time Only)
```bash
# 1. Run initial setup
python3 initial_setup.py

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings (database, API keys, etc.)

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Set up database
python3 quickstart.py --setup-db
```

### Daily Development Workflow
```bash
# Start development server
python3 quickstart.py --run

# Or use the interactive menu
python3 quickstart.py
```

## 📁 Project Structure

```
RouteForceRouting/
├── app/                    # Main application code
│   ├── config.py          # Configuration settings
│   ├── routes/            # Route handlers
│   ├── services/          # Business logic
│   └── models/            # Database models
├── routing/               # Core routing algorithms
├── migrations/            # Database migrations
├── uploads/               # File uploads
├── logs/                  # Application logs
├── .env                   # Environment configuration
├── initial_setup.py       # Initial project setup
├── quickstart.py          # Development helper
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables (.env file)
```bash
# Basic settings
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///routeforce.db

# Google Maps API
GOOGLE_MAPS_API_KEY=your-api-key

# Routing settings
MAX_ROUTE_OPTIMIZATION_TIME=300
MAX_STORES_PER_ROUTE=100
```

### Configuration Classes (app/config.py)
- `DevelopmentConfig`: For local development
- `ProductionConfig`: For production deployment
- `TestingConfig`: For running tests

## 🗄️ Database

### Setup
```bash
flask db init          # Initialize migrations (first time)
flask db migrate       # Create new migration
flask db upgrade        # Apply migrations
```

### Using the QuickStart Script
```bash
python3 quickstart.py --setup-db    # Does all the above
```

## 🧪 Testing

### Run Tests
```bash
# Using quickstart
python3 quickstart.py --test

# Manual
python3 -m pytest tests/ -v
```

### Test Files
- `test_*.py` files in the root directory
- `tests/` directory for organized test suites

## 🔍 Code Quality

### Linting and Formatting
```bash
# Run all quality checks
python3 quickstart.py --lint

# Format code
python3 quickstart.py --format

# Security scan
python3 quickstart.py --security
```

## 🚀 Deployment

### Local Development
```bash
python3 quickstart.py --run
# or
python3 app.py
# or
flask run
```

### Docker
```bash
docker-compose up -d
```

### Production
1. Set environment variables
2. Use production database (PostgreSQL recommended)
3. Configure Redis for caching
4. Set up proper logging
5. Use a production WSGI server (gunicorn)

## 🗺️ Google Maps API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable these APIs:
   - Maps JavaScript API
   - Directions API
   - Distance Matrix API
   - Places API
4. Create credentials (API key)
5. Add API key to `.env` file:
   ```
   GOOGLE_MAPS_API_KEY=your-api-key-here
   ```

## 🔒 Security

### API Keys and Secrets
- Never commit `.env` file to git
- Use environment variables for all secrets
- Rotate API keys regularly
- Use different keys for development/production

### Git Hooks
The setup script creates a pre-commit hook that:
- Checks for large files (>10MB)
- Warns about potential secret keys
- Ensures code quality

## 📊 Monitoring and Logging

### Logs
- Development: Console output
- Production: File-based logging
- Location: `logs/` directory

### Monitoring
- Prometheus metrics available
- Grafana dashboards configured
- Health check endpoints

## 🛠️ Useful Commands

### Development Helper
```bash
python3 quickstart.py              # Interactive menu
python3 quickstart.py --status     # Show project status
python3 quickstart.py --all        # Run complete setup
```

### Flask Commands
```bash
flask shell                        # Interactive shell
flask routes                       # Show all routes
flask db --help                   # Database commands
```

### Git Workflow
```bash
git status                         # Check status
git add .                         # Stage changes
git commit -m "message"           # Commit changes
git push                          # Push to remote
```

## 🆘 Troubleshooting

### Common Issues

#### "Command not found: python"
Use `python3` instead of `python` on macOS/Linux.

#### Database errors
```bash
# Reset database
rm -f *.db
python3 quickstart.py --setup-db
```

#### Import errors
```bash
# Reinstall dependencies
pip3 install -r requirements.txt
```

#### Port already in use
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

## 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Google Maps API: https://developers.google.com/maps
- Docker Documentation: https://docs.docker.com/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

---

For more help, run `python3 quickstart.py --help` or check the project documentation.
