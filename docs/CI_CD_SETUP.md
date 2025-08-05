# CI/CD Pipeline Documentation

This document describes the CI/CD pipeline setup for the RouteForceRouting project.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and provides automated testing, security scanning, building, and deployment for the RouteForceRouting application.

## Workflow File

The main CI/CD configuration is in `.github/workflows/ci-cd.yml`.

## Pipeline Stages

### 1. Testing (`test` job)
- **Triggers**: Push to main/develop branches, Pull requests
- **Python versions**: 3.11, 3.12
- **Steps**:
  - Code checkout
  - Python environment setup with caching
  - Dependency installation
  - Code linting with flake8 (syntax errors and basic issues)
  - Code formatting check with black (non-breaking)
  - Flask application import and configuration test
  - Basic health checks for key modules
  - Test execution with pytest

### 2. Security Scanning (`security` job)
- **Triggers**: Push and Pull request events
- **Steps**:
  - Trivy vulnerability scanner for filesystem
  - Results uploaded to GitHub Security tab
  - Continues on error to not block the pipeline

### 3. Build (`build` job)
- **Depends on**: test job success
- **Triggers**: Push events only
- **Steps**:
  - Production build testing
  - Build artifact creation with metadata
  - Artifact upload for deployment stages

### 4. Staging Deployment (`deploy-staging`)
- **Depends on**: test and build jobs
- **Triggers**: Push to develop branch
- **Environment**: staging
- **Steps**:
  - Artifact download
  - Simulated staging deployment

### 5. Production Deployment (`deploy-production`)
- **Depends on**: test and build jobs  
- **Triggers**: Push to main branch
- **Environment**: production
- **Steps**:
  - Artifact download
  - Simulated production deployment
  - Success notification

## Configuration Details

### Environment Variables
The pipeline uses the following environment variables:
- `FLASK_ENV`: Set to 'testing' for test jobs
- `DATABASE_URL`: SQLite memory database for testing
- `REDIS_URL`: Empty (disabled for testing)
- `SECRET_KEY`: Test secret key
- `RATELIMIT_STORAGE_URI`: Memory storage for rate limiting

### Testing Configuration
- Uses the `TestingConfig` class from `app.config`
- In-memory SQLite database
- Memory-based rate limiting (no Redis dependency)
- Null cache backend
- Disabled CSRF protection

### Linting and Quality Checks
- **flake8**: Checks for syntax errors, undefined names, and code quality
- **black**: Checks code formatting (non-breaking)
- Basic import and configuration validation

## Branch Strategy

- **main**: Production deployments
- **develop**: Staging deployments  
- **feature branches**: Testing only via pull requests

## Artifacts

Build artifacts include:
- Application code (`app/` directory)
- Python files and requirements
- Build metadata with commit and branch information

## Local Testing

To test CI/CD components locally:

```bash
# Test app import
FLASK_ENV=testing RATELIMIT_STORAGE_URI=memory:// python -c "
from app import create_app
app = create_app('testing')
print('✅ App created successfully')
"

# Test linting
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=node_modules,backup_deployment,migrations

# Test specific test module
FLASK_ENV=testing RATELIMIT_STORAGE_URI=memory:// python -m pytest routing/test/test_loader.py -v
```

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**: Ensure `RATELIMIT_STORAGE_URI=memory://` is set for testing
2. **Import Errors**: Check that all required modules exist and are properly structured
3. **Test Failures**: Review test configuration in `conftest.py` and ensure proper fixtures

### Pipeline Debugging

- Check Actions tab in GitHub repository for detailed logs
- Each job provides step-by-step execution details
- Failed jobs will show specific error messages and exit codes

## Future Enhancements

Potential improvements to the CI/CD pipeline:
- Add code coverage reporting
- Implement automated semantic versioning
- Add integration tests with external services
- Implement blue-green deployments
- Add performance benchmarking
- Implement database migration testing