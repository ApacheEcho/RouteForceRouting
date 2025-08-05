# Development Containers for RouteForce Routing

This directory contains the development container configuration for RouteForce Routing, providing a consistent and reproducible development environment.

## 🚀 Quick Start

### Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

### Getting Started

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/ApacheEcho/RouteForceRouting.git
   cd RouteForceRouting
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Reopen in Container**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Reopen in Container"
   - Select the command and wait for the container to build

4. **Configure your environment**:
   - Update `.env` file with your Google Maps API key
   - The setup script will guide you through the process

## 🛠️ What's Included

### Development Tools
- **Python 3.10** - Matching production runtime
- **Flask** - Web framework with hot reload
- **pytest** - Testing framework with coverage support
- **black** - Code formatter
- **flake8** - Linting and style checking
- **isort** - Import sorting

### VS Code Extensions
- Python language support with IntelliSense
- Testing integration
- Jupyter notebook support
- Docker integration
- GitHub Copilot (if available)
- Code formatting and linting

### Container Features
- **Port Forwarding**: 5000 (Flask), 8000 (alternative)
- **Volume Mounting**: Source code, uploads, environment files
- **Non-root User**: Secure development environment
- **Git Integration**: Pre-configured with GitHub CLI

## 📁 Configuration Files

- `devcontainer.json` - Main configuration for the dev container
- `Dockerfile` - Development-optimized container image
- `setup.sh` - Post-creation setup script
- `README.md` - This documentation

## 🔧 Customization

### Environment Variables

The dev container sets these environment variables by default:
- `PYTHONPATH=/app`
- `FLASK_ENV=development` 
- `FLASK_DEBUG=1`

### Port Configuration

Default ports forwarded from container to host:
- `5000` - Primary Flask application port
- `8000` - Alternative port for testing

### VS Code Settings

Pre-configured settings include:
- Black formatter with 88 character line length
- Flake8 linting enabled
- Pytest as the default test runner
- Auto-formatting on save
- Python path configuration

## 🧪 Testing Your Setup

After the container starts, run these commands to verify everything works:

```bash
# Check Python and dependencies
python --version
pip list

# Run tests
python -m pytest tests/ -v

# Start the development server
python app.py
```

The application should be available at http://localhost:5000

## 🐛 Troubleshooting

### Container Won't Start
- Ensure Docker Desktop is running
- Check that no other containers are using the same ports
- Try rebuilding: "Dev Containers: Rebuild Container"

### Missing API Keys
- Copy `.env.example` to `.env` if it exists
- Update `.env` with your Google Maps API credentials
- Restart the container after updating credentials

### Permission Issues
- The container runs as a non-root user (`appuser`)
- File permissions should be automatically configured
- If issues persist, rebuild the container

### Port Conflicts
- Change the forwarded ports in `devcontainer.json`
- Update the Flask app configuration accordingly

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
# Inside the container
pip install -r requirements.txt --upgrade
```

### Rebuilding the Container
When you modify the Dockerfile or devcontainer.json:
1. Press `Ctrl+Shift+P`
2. Select "Dev Containers: Rebuild Container"

### Adding VS Code Extensions
Edit the `extensions` array in `devcontainer.json` and rebuild.

## 🤝 Contributing

When contributing to the dev container configuration:

1. Test changes locally first
2. Document any new features or requirements
3. Update this README if needed
4. Ensure compatibility across different operating systems

## 📚 Additional Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Feature Reference](https://containers.dev/features)
- [RouteForce Routing Main README](../README.md)

---

🎉 **Happy coding!** The dev container provides everything you need to start contributing to RouteForce Routing immediately.