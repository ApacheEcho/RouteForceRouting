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

## Deployment

- Standard: Render (recommended). See `scripts/deploy-render.sh` and Render dashboard.
- Kubernetes: Removed from this repository to reduce complexity. If needed later, reintroduce via a dedicated branch.

## Setup

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

## Data Format

Your store data file should have columns: `Store Name`, `Address`.

## Contributing

- Fork, branch, commit, PR.

## License

Add your license information here.