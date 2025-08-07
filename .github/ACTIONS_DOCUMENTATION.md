# 🚀 GitHub Actions Documentation

## 📋 **Overview**
This document provides comprehensive information about the GitHub Actions workflows configured for RouteForce. Our CI/CD pipeline includes automated testing, security scanning, performance monitoring, and deployment management.

---

## 🏗️ **Workflow Architecture**

### **Core Workflows**

#### **1. CI/CD Pipeline** (`ci-cd.yml`)
**Purpose**: Primary continuous integration and deployment pipeline
- **Triggers**: Push to `main`/`develop`, Pull requests
- **Features**:
  - Multi-version Python testing (3.11, 3.12)
  - PostgreSQL and Redis service containers
  - Code formatting checks (Black)
  - Linting (Flake8) and type checking (MyPy)
  - Test coverage with Codecov integration
  - Docker image building and publishing
  - Automated deployment to staging

**Usage**:
```bash
# Workflow runs automatically on:
git push origin main
git push origin develop
# Opening/updating pull requests
```

#### **2. Security Scanning** (`Security.yml`)
**Purpose**: Comprehensive security analysis
- **Triggers**: Push to `main`, Pull requests
- **Features**:
  - Trivy filesystem scanning
  - SARIF report generation
  - Security event uploads
  - Vulnerability detection and reporting

#### **3. Performance Benchmarking** (`performance-benchmarks.yml`)
**Purpose**: Automated performance testing and monitoring
- **Triggers**: Push to main/develop, PRs, nightly schedule
- **Features**:
  - Route optimization algorithm benchmarking
  - Memory usage analysis
  - Performance comparison between branches
  - Automated PR comments with results

---

### **Advanced Workflows**

#### **4. Code Quality Gate** (`code-quality-gate.yml`)
**Purpose**: Comprehensive code quality enforcement
- **Triggers**: Pull requests, pushes to main/develop
- **Features**:
  - Black code formatting validation
  - Flake8 linting with detailed reports
  - MyPy type checking
  - Bandit security scanning
  - Safety dependency vulnerability checks
  - Code complexity analysis (Radon, Xenon)
  - Automated PR comments with quality reports
  - Blocking on critical issues

**Quality Checks**:
- ✅ **Formatting**: Black compliance required
- ✅ **Linting**: Flake8 compliance required  
- ⚠️ **Type Safety**: MyPy warnings logged
- 🔴 **Security**: Bandit issues block merge
- ⚠️ **Dependencies**: Safety warnings logged
- ⚠️ **Complexity**: Complexity warnings logged

#### **5. Release Management** (`release-management.yml`)
**Purpose**: Automated version management and releases
- **Triggers**: Git tags (`v*.*.*`), Manual workflow dispatch
- **Features**:
  - Semantic version bumping
  - Automated changelog generation
  - Docker image publishing with versioning
  - GitHub release creation with assets
  - Pre-release support
  - Staging deployment integration

**Manual Release**:
```bash
# Trigger via GitHub Actions UI:
# - Version type: patch/minor/major
# - Pre-release: true/false
```

#### **6. Auto-Update Dependencies** (`auto-update-dependencies.yml`)
**Purpose**: Automated dependency maintenance
- **Triggers**: Weekly schedule (Mondays 9 AM UTC), Manual dispatch
- **Features**:
  - Python package updates with `pur`
  - JavaScript/React Native package updates
  - GitHub Actions version updates
  - Automated testing of updates
  - PR creation with detailed change logs
  - Security vulnerability fixes

#### **7. System Monitoring** (`monitoring-health-checks.yml`)
**Purpose**: Proactive system health monitoring
- **Triggers**: Hourly health checks, 6-hourly comprehensive monitoring
- **Features**:
  - Infrastructure dependency health (GitHub API, Docker Hub, PyPI, npm)
  - Repository health validation
  - Dependency resolution checking
  - Workflow configuration validation
  - Security posture monitoring
  - Automated issue creation on critical failures

---

### **Specialized Workflows**

#### **8. PR Automation** (`pr-automation.yml`)
**Purpose**: Pull request lifecycle management
- **Features**:
  - Automated labeling based on file changes
  - Size classification (small/medium/large/epic)
  - First-time contributor welcoming
  - Issue linking validation
  - Security PR special handling

#### **9. Issue Automation** (`issue-automation.yml`)  
**Purpose**: Issue lifecycle management
- **Features**:
  - Smart auto-labeling based on content
  - Component-based assignment
  - Security issue prioritization
  - First-time contributor onboarding
  - Automated project board integration

#### **10. Project Automation** (`project-automation.yml`)
**Purpose**: GitHub Projects integration
- **Features**:
  - Automatic issue/PR addition to project boards
  - Status synchronization
  - Sprint planning support

---

## 🎛️ **Configuration Management**

### **Environment Variables**
```yaml
# Global Environment Variables
DOCKER_REGISTRY: ghcr.io
IMAGE_NAME: routeforce
PYTHON_VERSION: '3.12'
NODE_VERSION: '18'
```

### **Secrets Required**
- `GITHUB_TOKEN`: Automatic (provided by GitHub)
- `CODECOV_TOKEN`: For code coverage reporting
- `SLACK_WEBHOOK_URL`: For team notifications (optional)
- `DOCKER_REGISTRY_TOKEN`: For Docker publishing (if not using GITHUB_TOKEN)

### **Service Dependencies**
```yaml
# PostgreSQL Service
postgres:
  image: postgres:16
  env:
    POSTGRES_PASSWORD: postgres
    POSTGRES_DB: routeforce_test

# Redis Service  
redis:
  image: redis:7-alpine
```

---

## 🔧 **Workflow Triggers**

### **Automatic Triggers**
| Event | Workflows Triggered |
|-------|-------------------|
| Push to `main` | CI/CD, Security, Benchmarks, Monitoring |
| Push to `develop` | CI/CD, Quality Gate, Benchmarks |
| Pull Request | CI/CD, Quality Gate, PR Automation, Security |
| Schedule (Hourly) | Health Checks |
| Schedule (Daily) | Comprehensive Monitoring |
| Schedule (Weekly) | Dependency Updates |
| Git Tag `v*` | Release Management |

### **Manual Triggers**
All workflows support manual dispatch via GitHub Actions UI with customizable parameters.

---

## 📊 **Monitoring & Alerts**

### **Health Check Monitoring**
- **Infrastructure Dependencies**: GitHub API, Docker Hub, PyPI, npm Registry
- **Repository Health**: Critical files, dependency resolution
- **Workflow Health**: YAML validation, execution status
- **Security Posture**: Secret scanning, dependency vulnerabilities

### **Performance Monitoring**
- **Algorithm Performance**: Genetic algorithm, simulated annealing benchmarks
- **Memory Usage**: Optimization process memory profiling
- **Response Times**: API endpoint performance tracking
- **Regression Detection**: Performance comparison across commits

### **Quality Monitoring**
- **Code Coverage**: Automated tracking with Codecov
- **Code Quality**: Continuous assessment with quality gates
- **Security Scanning**: Vulnerability detection and tracking
- **Dependency Health**: Automated security and compatibility checks

---

## 🚦 **Status & Badges**

Add these badges to your README:

```markdown
![CI/CD](https://github.com/ApacheEcho/RouteForceRouting/workflows/RouteForce%20CI/CD%20Pipeline/badge.svg)
![Security](https://github.com/ApacheEcho/RouteForceRouting/workflows/Security%20Scanning/badge.svg)
![Quality](https://github.com/ApacheEcho/RouteForceRouting/workflows/Code%20Quality%20Gate/badge.svg)
![Performance](https://github.com/ApacheEcho/RouteForceRouting/workflows/Performance%20Benchmarking/badge.svg)
```

---

## 🛠️ **Maintenance**

### **Weekly Tasks**
- Review dependency update PRs
- Check performance benchmark trends
- Review security scan results
- Update workflow configurations as needed

### **Monthly Tasks**
- Update GitHub Actions versions
- Review and optimize workflow performance
- Update documentation
- Security policy review

### **Troubleshooting Common Issues**

#### **Workflow Failures**
```bash
# Check workflow logs
gh run list --workflow=ci-cd.yml --limit=10
gh run view [RUN_ID] --log

# Re-run failed jobs
gh run rerun [RUN_ID] --failed
```

#### **Performance Issues**
```bash
# Check recent benchmark results
gh run list --workflow=performance-benchmarks.yml --limit=5

# Download benchmark artifacts
gh run download [RUN_ID]
```

#### **Security Alerts**
```bash
# List security advisories
gh api repos/ApacheEcho/RouteForceRouting/security-advisories

# Check Dependabot alerts
gh api repos/ApacheEcho/RouteForceRouting/dependabot/alerts
```

---

## 🎯 **Best Practices**

### **For Developers**
1. **Pre-commit Setup**: Install pre-commit hooks for local quality checks
2. **Branch Naming**: Use descriptive names (`feature/`, `bugfix/`, `hotfix/`)
3. **Commit Messages**: Follow conventional commit format
4. **PR Guidelines**: Use PR templates, link issues, add descriptions

### **For Maintainers**
1. **Workflow Updates**: Test in feature branches before merging
2. **Secret Management**: Rotate secrets regularly, use minimal permissions
3. **Performance Monitoring**: Review benchmark trends weekly
4. **Security Reviews**: Address security alerts promptly

### **For Operations**
1. **Monitoring**: Check health dashboards regularly
2. **Capacity Planning**: Monitor runner usage and costs
3. **Backup**: Ensure workflow configurations are backed up
4. **Disaster Recovery**: Have rollback procedures documented

---

## 📚 **Additional Resources**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [RouteForce Development Guide](DEVELOPMENT.md)
- [Security Policy](SECURITY.md)

---

**Last Updated**: August 2025  
**Maintained By**: RouteForce Development Team
