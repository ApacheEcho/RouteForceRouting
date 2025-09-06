# Docker Setup Instructions for RouteForce Routing

## 🐳 Docker Deployment Options

### Option 1: Full Production Setup (Requires Docker Desktop)

If you have Docker Desktop installed and running:

```bash
# Start Docker Desktop first, then:
docker-compose up --build
```

This will start:
- Flask application on port 5000
- Redis cache on port 6379  
- Nginx reverse proxy on port 80/443

### Option 2: Simplified Docker Setup

If you want a simpler setup without Redis and Nginx:

```bash
# Use the simplified compose file:
docker-compose -f docker-compose.simple.yml up --build
```

### Option 3: Direct Python Execution (No Docker)

If Docker is not available or you prefer direct execution:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py

# Or on a different port if 5000 is busy:
PORT=5001 python app.py

## ⚙️ Gunicorn Runtime Configuration (Docker)

The production image uses Gunicorn and respects these environment variables:

```
PORT=5000                # Bind port (defaults to 5000)
GUNICORN_WORKERS=4       # Worker processes
GUNICORN_LOG_LEVEL=info  # Log level (debug|info|warning|error)
```

You can override them in your compose file or environment.
```

## 🔧 Docker Setup Instructions

### For macOS:

1. **Install Docker Desktop:**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Ensure Docker is running (check the menu bar icon)

2. **Start the Application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the Application:**
   - Main App: http://localhost
   - Dashboard: http://localhost/dashboard
   - Direct Flask: http://localhost:5000

### For Linux:

1. **Install Docker:**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Install Docker Compose:**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Start the Application:**
   ```bash
   docker-compose up --build
   ```

## 🚀 Current Application Status

The RouteForce Routing application is enterprise-ready with:

- ✅ Real-time dashboard with interactive maps
- ✅ Proximity clustering algorithms
- ✅ RESTful API endpoints
- ✅ Comprehensive test suite (55 tests)
- ✅ Production-ready Docker configuration
- ✅ 10/10 architecture validation

## 🌐 Access URLs

Once running:

- **Main Application:** http://localhost:5000 (or your chosen port)
- **Interactive Dashboard:** http://localhost:5000/dashboard
- **API Health Check:** http://localhost:5000/api/v1/health
- **Prometheus Metrics:** http://localhost:5000/metrics

## 🛠️ Troubleshooting

### Port Already in Use:
```bash
# Kill processes using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
PORT=5001 python app.py
```

### Docker Issues:
```bash
# Check Docker status
docker --version
docker info

# Start Docker service (Linux)
sudo systemctl start docker

# Restart Docker Desktop (macOS)
# Use the Docker Desktop application
```

### Missing Dependencies:
```bash
# Reinstall requirements
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📊 Available Demo Scripts

Run these to see the application in action:

```bash
# Full enterprise demo
./demo_enterprise.sh

# Enhanced dashboard demo
./demo_dashboard_enhanced.sh

# Architecture validation
python validate_architecture.py
```

## 🎯 Quick Test

Verify everything is working:

```bash
# Run tests
python -m pytest -v

# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/v1/health
```
