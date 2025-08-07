# GitHub Codespaces Configuration for RouteForceRouting

## 🚀 Quick Start

This repository is configured for **GitHub Codespaces** with a complete development environment including:

- **Python 3.12** with all project dependencies
- **PostgreSQL 16** database with PostGIS extension  
- **Redis 7** for caching and sessions
- **PgAdmin 4** for database management
- **Docker** support for containerized development
- **VS Code extensions** for Python, Git, Docker, and GitHub integration

## 🔧 Getting Started

### Option 1: Create Codespace (Recommended)
1. Click the **Code** button on GitHub
2. Select **Codespaces** tab
3. Click **Create codespace on main**
4. Wait for the environment to build (3-5 minutes)

### Option 2: Using GitHub CLI
```bash
gh codespace create --repo ApacheEcho/RouteForceRouting
```

## 🏗️ Environment Details

### Pre-installed Tools
- **Python 3.12** with pip, venv, and development tools
- **Node.js LTS** with npm for frontend tooling
- **Docker** & Docker Compose for containerization
- **GitHub CLI** for repository management
- **PostgreSQL Client** for database operations
- **Redis Tools** for cache management

### VS Code Extensions
- Python development (linting, formatting, testing)
- Docker support
- GitHub Copilot & Copilot Chat
- GitLens for advanced Git features
- REST Client for API testing
- And many more for enhanced productivity

### Available Services

| Service | Port | URL | Credentials |
|---------|------|-----|-------------|
| Flask App | 5000 | http://localhost:5000 | - |
| PgAdmin | 8080 | http://localhost:8080 | admin@routeforce.local / admin |
| PostgreSQL | 5432 | localhost:5432 | routeforce / password |
| Redis | 6379 | localhost:6379 | - |

## 🛠️ Development Commands

The environment includes helpful aliases for common tasks:

### Application Commands
```bash
rf-run          # Start Flask development server
rf-test         # Run test suite
rf-test-cov     # Run tests with coverage
rf-lint         # Check code quality
rf-format       # Format code (black + isort)
rf-shell        # Open Flask shell with app context
```

### Database Commands
```bash
rf-db-migrate   # Create new migration
rf-db-upgrade   # Apply migrations
```

### Docker Commands
```bash
dcup            # Start all services
dcdown          # Stop all services  
dcbuild         # Rebuild containers
dclogs          # View service logs
```

## 🗄️ Database Setup

The environment automatically creates three databases:
- `routeforce_dev` - Development database
- `routeforce_test` - Testing database  
- `routeforce_staging` - Staging database

All databases include:
- **PostGIS** extension for geospatial data
- **uuid-ossp** extension for UUID generation

## 📝 Configuration Files

### Environment Variables
The `.env` file is automatically created with development defaults:

```bash
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=postgresql://routeforce:password@postgres:5432/routeforce_dev
REDIS_URL=redis://redis:6379/0
```

**⚠️ Important**: Update API keys and secrets in `.env` for full functionality.

### Available Databases
- **Development**: `postgresql://routeforce:password@postgres:5432/routeforce_dev`
- **Testing**: `postgresql://routeforce:password@postgres:5432/routeforce_test`  
- **Staging**: `postgresql://routeforce:password@postgres:5432/routeforce_staging`

## 🚀 First Run

After the Codespace loads:

1. **Check services status**:
   ```bash
   # Services start automatically - check status in terminal
   ```

2. **Install dependencies** (if needed):
   ```bash
   rf-deps
   ```

3. **Run database migrations**:
   ```bash
   rf-db-upgrade
   ```

4. **Start the application**:
   ```bash
   rf-run
   ```

5. **Open your app**: VS Code will automatically forward port 5000

## 🔧 Customization

### Adding VS Code Extensions
Edit `.devcontainer/devcontainer.json` and add extension IDs to the `extensions` array.

### Installing Additional Tools
Modify `.devcontainer/Dockerfile` to add system packages or `.devcontainer/postCreateCommand.sh` for setup scripts.

### Environment Variables
Update `.devcontainer/devcontainer.json` `containerEnv` section or modify the generated `.env` file.

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check service status
docker-compose ps

# Restart services
dcdown && dcup

# View logs
dclogs
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
pg_isready -h postgres -p 5432 -U routeforce

# Test Redis connection
redis-cli -h redis ping
```

### Permission Issues
```bash
# Fix file permissions
chmod +x scripts/*.sh
chmod +x .devcontainer/*.sh
```

## 🌟 Features

### Automatic Setup
- Pre-commit hooks installation
- Database initialization with extensions
- Environment file creation
- Development aliases configuration

### Integrated Development
- **IntelliSense** for Python with type hints
- **Debugging** configuration for Flask apps
- **Testing** integration with pytest
- **Git** integration with GitLens
- **Docker** support for containerized development

### Database Management
- **PgAdmin** web interface for PostgreSQL
- **Redis** CLI tools for cache management
- **Automatic migrations** on startup
- **Multiple environments** (dev/test/staging)

## 📚 Additional Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Dev Container Reference](https://containers.dev/implementors/json_reference/)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)

## 🤝 Contributing

This Codespaces configuration is designed to provide a consistent development environment for all contributors. If you need additional tools or configurations, please update the dev container configuration and submit a pull request.

---

**🎉 Happy Coding!** Your complete RouteForceRouting development environment is ready to go!
