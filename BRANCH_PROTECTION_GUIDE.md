# Branch Protection Rules Configuration Guide

This document describes the branch protection rules that should be configured for the `main` branch to ensure code quality and security.

## Required GitHub Branch Protection Settings

The following settings should be configured in the GitHub repository settings under `Settings > Branches > Add rule` for the `main` branch:

### 1. Basic Protection Rules

- **Branch name pattern**: `main`
- **Restrict pushes that create files larger than 100MB**: ✅ Enabled
- **Restrict force pushes**: ✅ Enabled  
- **Restrict deletions**: ✅ Enabled

### 2. Pull Request Requirements

- **Require a pull request before merging**: ✅ Enabled
  - **Require approvals**: ✅ Enabled
    - **Required number of reviewers before merging**: `1` (minimum recommended)
    - **Dismiss stale PR approvals when new commits are pushed**: ✅ Enabled
    - **Require review from code owners**: ✅ Enabled (if CODEOWNERS file exists)
  - **Restrict approvals to users with push access**: ✅ Enabled
  - **Allow specified actors to bypass required pull requests**: ❌ Disabled

### 3. Status Check Requirements

- **Require status checks to pass before merging**: ✅ Enabled
  - **Require branches to be up to date before merging**: ✅ Enabled
  - **Required status checks**:
    - `lint` (from lint.yml workflow)
    - `test (3.11)` (from test.yml workflow)  
    - `test (3.12)` (from test.yml workflow)
    - `test` (from ci-cd.yml workflow)
    - `security` (from ci-cd.yml workflow)

### 4. Additional Security Settings

- **Require conversation resolution before merging**: ✅ Enabled
- **Do not allow bypassing the above settings**: ✅ Enabled
- **Allow force pushes**: ❌ Disabled
- **Allow deletions**: ❌ Disabled

## Workflow Status Checks

The following GitHub Actions workflows provide status checks that are required for branch protection:

### 1. Lint Workflow (`.github/workflows/lint.yml`)
- **Purpose**: Code quality and formatting checks
- **Checks performed**:
  - Import organization with `isort`
  - Code formatting with `black`
  - Code linting with `flake8`
  - Type checking with `mypy` (optional)
- **Triggers**: Push and PR to `main` and `develop` branches

### 2. Test Workflow (`.github/workflows/test.yml`)
- **Purpose**: Application testing and functionality verification
- **Checks performed**:
  - Unit tests with `pytest`
  - Multi-version testing (Python 3.11, 3.12)
  - Module import validation
  - Application startup verification
- **Triggers**: Push and PR to `main` and `develop` branches

### 3. CI/CD Workflow (`.github/workflows/ci-cd.yml`)
- **Purpose**: Comprehensive testing, security, and deployment
- **Checks performed**:
  - Full test suite with coverage
  - Security scanning with Trivy
  - Docker image building
  - Deployment to staging/production
- **Triggers**: Push and PR to `main` and `develop` branches

## Configuration Steps

1. **Navigate to Repository Settings**:
   - Go to `https://github.com/ApacheEcho/RouteForceRouting/settings/branches`

2. **Add Branch Protection Rule**:
   - Click "Add rule"
   - Enter "main" as the branch name pattern

3. **Configure Settings**:
   - Enable all settings listed above
   - Add the required status checks listed above

4. **Save Configuration**:
   - Click "Create" to save the branch protection rule

## Verification

After configuring branch protection rules, verify they are working by:

1. **Testing PR Requirements**:
   - Create a test branch
   - Make a small change and create a PR to main
   - Verify that status checks run and are required
   - Verify that approval is required before merging

2. **Testing Direct Push Prevention**:
   - Try to push directly to main branch
   - Verify that the push is rejected

3. **Testing Status Check Requirements**:
   - Create a PR with failing tests
   - Verify that merge is blocked until tests pass

## Benefits

These branch protection rules provide:

- **Code Quality**: Ensure all code is reviewed and tested before merging
- **Security**: Prevent unauthorized changes and vulnerabilities
- **Stability**: Maintain stable main branch with working code
- **Collaboration**: Enforce proper review process for all changes
- **Compliance**: Meet industry standards for code review and quality

## Maintenance

- **Review Requirements Regularly**: Adjust number of required reviewers as team grows
- **Update Status Checks**: Add new workflow checks as they are created
- **Monitor Workflow Health**: Ensure required workflows are maintained and functional
- **Team Training**: Ensure all team members understand the process

## Emergency Procedures

For urgent hotfixes that need to bypass normal process:

1. **Admin Override**: Repository admins can temporarily disable protection rules
2. **Hotfix Branch**: Create hotfix branch from main, fix issue, create emergency PR
3. **Expedited Review**: Get expedited review and approval for critical fixes
4. **Re-enable Protection**: Always re-enable protection rules after emergency

## Additional Resources

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Best Practices for Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches#best-practices-for-protected-branches)