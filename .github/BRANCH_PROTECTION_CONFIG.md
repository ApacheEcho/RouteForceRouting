# Branch Protection Rules Configuration

This document outlines the required branch protection rules for the `main` branch to ensure code quality and security as requested in issue #30.

## Required Branch Protection Settings

### 1. Pull Request Requirements
- **Require pull request reviews before merging**: ✅ Required
- **Required number of reviewers**: 1 (minimum)
- **Dismiss stale PR reviews when new commits are pushed**: ✅ Enabled
- **Require review from code owners**: ✅ Enabled (when CODEOWNERS file exists)

### 2. Status Checks Requirements
The following status checks must pass before merging:

#### CI/CD Pipeline Checks
- `test (3.11)` - Python 3.11 test suite
- `test (3.12)` - Python 3.12 test suite
- `security` - Security vulnerability scanning
- `build` - Docker image build validation

#### Code Quality Checks
- Code formatting check (black)
- Linting check (flake8)
- Type checking (mypy)
- Security scan (bandit)

### 3. Additional Protection Rules
- **Require branches to be up to date before merging**: ✅ Enabled
- **Require linear history**: ✅ Enabled (prevents merge commits)
- **Include administrators**: ✅ Enabled (applies rules to admin users)
- **Allow force pushes**: ❌ Disabled
- **Allow deletions**: ❌ Disabled

## Implementation Steps

### Step 1: Repository Settings Configuration
Navigate to repository Settings → Branches → Add rule or edit existing rule for `main` branch.

### Step 2: Configure Required Status Checks
Select the following status checks as required:
```
RouteForce CI/CD Pipeline / test (3.11)
RouteForce CI/CD Pipeline / test (3.12)
RouteForce CI/CD Pipeline / security
RouteForce CI/CD Pipeline / build
```

### Step 3: Set Up Code Owners (Recommended)
Create a `.github/CODEOWNERS` file to specify code review requirements:
```
# Global code owners
* @ApacheEcho

# Specific areas
/.github/ @ApacheEcho
/app/ @ApacheEcho
/routing/ @ApacheEcho
/tests/ @ApacheEcho
```

### Step 4: Verify Configuration
1. Create a test pull request
2. Verify that all required status checks appear
3. Confirm that merge is blocked until all checks pass
4. Test that review requirements are enforced

## Status Check Details

### Test Suite (`test`)
- Runs comprehensive test suite on Python 3.11 and 3.12
- Includes unit tests, integration tests, and coverage reporting
- Must achieve minimum test coverage threshold
- Includes database and Redis service testing

### Security Scanning (`security`)
- Trivy vulnerability scanner for dependencies and container images
- Bandit security linting for Python code
- SARIF results uploaded to GitHub Security tab
- Zero high-severity vulnerabilities required

### Build Validation (`build`)
- Docker image build and push to registry
- Multi-architecture build support
- SBOM (Software Bill of Materials) generation
- Container security validation

## Emergency Procedures

### Bypass Procedures (Admin Only)
In case of emergency deployments or critical hotfixes:
1. Administrator can temporarily disable protection rules
2. Make necessary changes with proper documentation
3. Re-enable protection rules immediately after deployment
4. Create follow-up PR to ensure changes go through normal review process

### Troubleshooting Failed Status Checks
1. **Test Failures**: Review test logs, fix failing tests, push new commit
2. **Security Issues**: Address vulnerabilities in dependencies or code
3. **Build Failures**: Fix Docker configuration or build scripts
4. **Formatting Issues**: Run `black .` and `flake8` locally before pushing

## Monitoring and Maintenance

### Regular Reviews
- Monthly review of protection rules effectiveness
- Quarterly update of required status checks
- Annual review of code owners and permissions

### Metrics Tracking
- Pull request merge time
- Failed status check frequency
- Security vulnerability resolution time
- Code review participation rates

## Additional Security Measures

### Secret Scanning
- GitHub secret scanning enabled
- Custom secret patterns configured
- Immediate notifications for exposed secrets
- Automatic resolution tracking

### Dependency Management
- Dependabot enabled for automatic security updates
- Regular dependency audits
- Pin exact versions in production deployments
- Monitor for deprecated packages

---

**Implementation Date**: To be set when rules are applied  
**Last Updated**: Initial version  
**Next Review**: 30 days after implementation  
**Responsible Team**: @ApacheEcho