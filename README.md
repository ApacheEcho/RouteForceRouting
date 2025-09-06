# RouteForceRouting

[![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-blue?logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=ApacheEcho/RouteForceRouting)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-46e3b7.svg)](https://render.com/deploy?repo=https://github.com/ApacheEcho/RouteForceRouting)
[![CI/CD Pipeline](https://github.com/ApacheEcho/RouteForceRouting/workflows/RouteForce%20CI%2FCD%20Pipeline/badge.svg)](https://github.com/ApacheEcho/RouteForceRouting/actions)
[![codecov](https://codecov.io/gh/ApacheEcho/RouteForceRouting/branch/main/graph/badge.svg)](https://codecov.io/gh/ApacheEcho/RouteForceRouting)

A route optimization engine for field execution teams. This application helps optimize routes for visiting multiple locations efficiently.

## 🚀 Quick Start

### GitHub Codespaces (Recommended)
Get started instantly with a fully configured development environment:

[![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-blue?logo=github&style=for-the-badge)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=ApacheEcho/RouteForceRouting)

**What you get:**
- ✅ Python 3.12 with all dependencies pre-installed
- ✅ PostgreSQL + Redis databases ready to use
- ✅ VS Code with optimal extensions
- ✅ Pre-commit hooks configured
- ✅ Development aliases and shortcuts
- ✅ PgAdmin for database management

**Ready in 3-5 minutes!** No local setup required.

## 🚨 Security Notice

- Do not commit API keys or passwords.
- Use environment variables for secrets. See `.env.example` and `.env.production.template` for placeholders.
- Rotate any previously exposed keys.

## ✅ Improvements

- Geocoding cache to reduce API calls
- `.gitignore` hardened for env files
- Error handling and UI polish

## 📋 Current Status

Pre-alpha capabilities:
- Data loading and validation (CSV/Excel)
- Geocoding with caching
- Basic route optimization
- Google Maps link generation

## Setup
## 🛠️ Expanding MCP Server Scope & Advanced Features

The Model Context Protocol (MCP) Filesystem Server restricts file operations to specific directories for security. By default, it allows access to the project root and its parent directory. To enable advanced automation and context-aware development across more of your system, you can expand the allowed directories as follows:

### How to Expand Allowed Directories

1. **Edit the MCP server startup command** to include additional allowed paths. For example:

	```bash
	node mcp-server/build/filesystem.js /Users/frank /Users/frank/RouteForceRouting /any/other/path
	```

	Or, if using the provided script, edit `mcp-server/start-filesystem-server.sh` to add extra arguments:

	```bash
	#!/bin/bash
	node mcp-server/build/filesystem.js /Users/frank /Users/frank/RouteForceRouting
	```

2. **Restart the MCP server** after making changes.

3. **All advanced file operations** (read, write, search, create, delete, stats) are now available within the expanded set of allowed directories.

> **Note:** The `mcp.yaml` file does NOT control allowed directories. Allowed paths are set at server startup only.

### Troubleshooting

- If you see "Path not allowed" errors, confirm the directory is included in the startup command.
- For security, only add trusted directories.

---

### Prerequisites

```bash
python3 --version
pip install -r requirements.txt
```

### Environment

1. Copy `.env.example` to `.env` for local development and set values.
2. For production, use `.env.production.template` as a reference and configure real values via your hosting provider's environment settings (e.g., Render). Do not commit real secrets.

### Run

```bash
python app.py
```

Defaults
- Port: uses `PORT` if set; otherwise 5000 in development, 8000 in production
- Cache: `CACHE_TYPE` accepts shorthand values `redis`, `simple`, or `null` and maps to the proper Flask-Caching backend automatically
- Redis: if `CACHE_REDIS_URL` is not set, it falls back to `REDIS_URL`

## Data Format

Your store data file should have columns: `Store Name`, `Address`.

## Contributing

- Fork, branch, commit, PR.

## License

Add your license information here.
