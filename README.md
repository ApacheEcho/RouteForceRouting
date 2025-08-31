# RouteForceRouting

[![Open in GitHub Codespaces](https://img.shields.io/badge/Open%20in-Codespaces-blue?logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=ApacheEcho/RouteForceRouting)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20to-Render-46e3b7.svg)](https://render.com/deploy?repo=https://github.com/ApacheEcho/RouteForceRouting)
[![CI/CD Pipeline](https://github.com/ApacheEcho/RouteForceRouting/workflows/RouteForce%20CI%2FCD%20Pipeline/badge.svg)](https://github.com/ApacheEcho/RouteForceRouting/actions)
[![codecov](https://codecov.io/gh/ApacheEcho/RouteForceRouting/branch/main/graph/badge.svg)](https://codecov.io/gh/ApacheEcho/RouteForceRouting)

A comprehensive route optimization platform for field execution teams with AI-powered analytics, real-time optimization, and MCP server integration.

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
- ✅ **MCP Server** for AI integration

**Ready in 3-5 minutes!** No local setup required.

## 🤖 MCP Server Integration

RouteForce includes a **Model Context Protocol (MCP) server** for seamless AI integration:

### Features:
- **Route Optimization**: Multiple algorithms (genetic, simulated annealing, multi-objective)
- **Real-time Analytics**: Performance metrics and route analysis
- **Demand Prediction**: ML-powered forecasting
- **Delivery Reports**: Comprehensive reporting capabilities

### Quick Setup:
```bash
cd mcp-server
npm install
npm run build
npm start
```

### VS Code Integration:
The MCP server is pre-configured for VS Code debugging. Use the `.vscode/mcp.json` configuration to connect AI tools directly to RouteForce capabilities.

### Preview Models (optional)
If your team wants to try preview or experimental models (for example `copilot/gpt-5-mini-preview`), see `.github/CODELLAUNCH.md` for workspace and user opt-in instructions, repository trust guidance, and an admin request template.

For tuning Beast Mode to use GPT-5 Mini (recommended for short, low-latency tasks), see `docs/BEASTMODE_GPT5_MINI.md`.

## 🚨 Security Notice

- Do not commit API keys or passwords.
- Use environment variables for secrets. See `.env.example` and `.env.production.template` for placeholders.
- Rotate any previously exposed keys.

## ✅ Current Features

**Production-Ready Platform:**
- **Multi-Algorithm Optimization**: Genetic algorithms, simulated annealing, multi-objective optimization
- **Real-time WebSocket Updates**: Live route optimization progress
- **Comprehensive API**: 19+ endpoints with full Swagger documentation
- **ML Integration**: Predictive analytics and demand forecasting
- **Performance Monitoring**: Sentry integration with custom metrics
- **Production Deployment**: Live on Render with auto-scaling

**Technical Stack:**
- **Backend**: Python Flask + SQLAlchemy + Redis
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: Flask-SocketIO with WebSocket support
- **AI/ML**: Scikit-learn integration with predictive models
- **Monitoring**: Sentry error tracking and performance monitoring

## 🔧 Development

### Local Setup:
```bash
# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Setup environment
cp .env.example .env

# Run development server
python app.py

# Setup MCP Server
cd mcp-server && npm install && npm run build
```

### API Documentation:
- **Swagger UI**: `/api/docs`
- **OpenAPI Spec**: `/api/swagger.json`
- **Health Check**: `/api/v1/health`

## Deployment

- **Production**: Deployed on Render platform with auto-scaling
- **CI/CD**: GitHub Actions with comprehensive testing
- **Monitoring**: Sentry integration for error tracking and performance monitoring

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