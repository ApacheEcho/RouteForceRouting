# GitHub Codespaces Configuration for RouteForceRouting

This directory contains VS Code workspace configurations optimized for GitHub Codespaces.

## 📁 Configuration Files

### Core Codespaces Files
- **`extensions.json`** - Pre-installed extensions for Codespaces
- **`settings.json`** - VS Code settings optimized for remote development
- **`launch.json`** - Debug configurations for Python/Flask
- **`tasks.json`** - Build and development tasks
- **`ports.json`** - Port forwarding configuration

## 🔧 Extensions Configured

### GitHub Integration
- `GitHub.codespaces` - Core Codespaces functionality
- `GitHub.vscode-pull-request-github` - Pull request management
- `GitHub.copilot` + `GitHub.copilot-chat` - AI assistance
- `github.vscode-github-actions` - Workflow management

### Python Development
- `ms-python.python` - Core Python support
- `ms-python.debugpy` - Python debugging
- `ms-python.black-formatter` - Code formatting
- `ms-python.flake8` - Linting
- `ms-toolsai.jupyter` - Notebook support

### DevOps & Remote Development
- `ms-azuretools.vscode-docker` - Container support
- `ms-vscode-remote.remote-containers` - Container development
- `ms-vscode.remote-repositories` - Remote repository access

## 🚀 Quick Start Tasks

Use `Ctrl/Cmd + Shift + P` and search for "Tasks: Run Task":

- **🚀 Start Flask App (Codespaces)** - Launch development server
- **🧪 Run Tests (Codespaces)** - Execute test suite
- **🔧 Install Dependencies** - Install Python packages
- **🔍 Check Service Health** - Verify PostgreSQL/Redis

## 🔗 Port Forwarding

Automatically configured ports:
- **5000** - Flask application (auto-opens browser)
- **8080** - PgAdmin interface (opens in preview)
- **5432** - PostgreSQL (private access)
- **6379** - Redis (private access)

## ⚙️ Debug Configurations

Available debug configs in `launch.json`:
- **Python: Flask App (Codespaces)** - Debug main application
- **Python: Debug Tests (Codespaces)** - Debug test suite
- **Python: Current File (Codespaces)** - Debug active file
- **Docker: Attach to Python Container** - Container debugging

## 🎯 Optimizations

### Performance
- Reduced memory usage for large projects
- Optimized search/indexing exclusions
- Minimal UI distractions

### Remote Development
- Auto port forwarding
- Smart Git integration
- Persistent session configuration

### Python Environment
- Configured for `/usr/local/bin/python`
- Environment variables for Flask/DB
- Test discovery and coverage

## 📝 Usage Tips

### Starting Development
```bash
# Services start automatically, then:
Ctrl/Cmd + Shift + P → "Tasks: Run Task" → "🚀 Start Flask App (Codespaces)"
```

### Debugging
1. Set breakpoints in Python code
2. Press `F5` or use Debug panel
3. Select "Python: Flask App (Codespaces)"

### Testing
```bash
Ctrl/Cmd + Shift + P → "Tasks: Run Task" → "🧪 Run Tests (Codespaces)"
```

### Port Access
- VS Code automatically forwards configured ports
- Check **PORTS** tab in integrated terminal
- Click globe icon to open in browser

## 🔧 Customization

### Adding Extensions
Edit `extensions.json` and add extension IDs to the `recommendations` array.

### Changing Settings
Modify `settings.json` - changes apply to Codespaces workspace.

### Custom Tasks
Add tasks to `tasks.json` for project-specific commands.

### Port Configuration
Update `ports.json` to modify forwarding behavior.

---

**Ready to code!** 🎉 Your Codespaces environment is optimized for RouteForceRouting development.
