# GitHub Codespaces Development Environment

This directory contains the configuration for GitHub Codespaces, providing a cloud-based development environment for the RouteForce Routing application.

## What's Included

### `devcontainer.json`
Main configuration file that sets up:
- **Python 3.12** runtime environment
- **VS Code extensions** for Python development (linting, formatting, debugging)
- **Port forwarding** for Flask development (5000, 8000) and Redis (6379)
- **Environment variables** for development mode
- **Code formatting** and linting configuration

### `postCreateCommand.sh`
Automated setup script that runs after container creation:
- Installs Python dependencies from `requirements.txt`
- Creates necessary directories (`uploads`, `instance`, `logs`)
- Generates a sample `.env` file with configuration templates
- Validates the Flask application setup
- Provides quick start instructions

## Getting Started with Codespaces

1. **Open in Codespaces**: Click the "Code" button on GitHub and select "Create codespace on main"

2. **Wait for setup**: The environment will automatically install dependencies (takes 2-3 minutes)

3. **Configure your environment**:
   - Edit the `.env` file with your actual Google Maps API key
   - The file is created automatically with helpful comments

4. **Start developing**:
   ```bash
   # Run the development server
   python app.py
   
   # Run tests
   python -m pytest
   
   # Format code
   black .
   
   # Lint code
   flake8 .
   ```

## Features Available

### Pre-installed Tools
- Python 3.12 with all project dependencies
- Git and GitHub CLI
- VS Code with Python development extensions
- Code formatting (Black) and linting (Flake8)
- Testing framework (pytest)

### Port Forwarding
- **Port 5000**: Flask app (production mode)
- **Port 8000**: Flask app (development mode)  
- **Port 6379**: Redis (if using caching features)

### VS Code Extensions
- Python language support with IntelliSense
- Code formatting on save
- Integrated linting and error detection
- Jupyter notebook support for data analysis
- JSON and web development tools

## Development Workflow

1. **Code changes** are automatically formatted on save
2. **Linting errors** are highlighted in the editor
3. **Tests** can be run from the integrated terminal
4. **Flask app** can be started and accessed via forwarded ports
5. **Environment variables** are loaded from the `.env` file

## Optional Services

The basic Codespaces setup works without external dependencies. For full functionality:

- **Redis**: Required for caching and rate limiting features
- **PostgreSQL**: Required for database persistence features  

These can be added later via docker-compose if needed for specific development tasks.

## Troubleshooting

If you encounter issues:

1. **Dependencies fail to install**: Check the terminal output during setup
2. **Flask app won't start**: Ensure your `.env` file has valid configuration
3. **Port forwarding issues**: Verify ports 5000/8000 are properly forwarded in Codespaces
4. **API errors**: Add your Google Maps API key to the `.env` file

For additional help, check the main project README.md or open an issue.