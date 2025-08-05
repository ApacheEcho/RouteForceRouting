# CodeQL Security Analysis

This repository is configured with GitHub CodeQL analysis to automatically detect security vulnerabilities and code quality issues.

## Overview

CodeQL is GitHub's semantic code analysis engine that treats code as data and runs queries to find vulnerabilities. Our setup analyzes both Python and JavaScript/TypeScript code across the entire repository.

## Configuration

### Workflow Triggers
- **Push events**: Runs on pushes to `main` and `develop` branches
- **Pull requests**: Runs on PRs targeting `main` and `develop` branches  
- **Scheduled scans**: Weekly runs every Monday at 6:42 PM UTC

### Languages Analyzed
- **Python**: Backend Flask application, ML models, routing algorithms
- **JavaScript/TypeScript**: React frontend and PWA mobile app

### Security Query Suites
- `security-extended`: Comprehensive security vulnerability detection
- `security-and-quality`: Security issues plus code quality checks

## What CodeQL Detects

### Python Security Issues
- SQL injection vulnerabilities
- Command injection flaws
- Path traversal attacks
- Hardcoded credentials
- Unsafe deserialization
- LDAP injection
- NoSQL injection
- Regular expression DoS (ReDoS)

### JavaScript/TypeScript Security Issues
- Cross-site scripting (XSS)
- Prototype pollution
- Code injection via eval()
- DOM-based XSS
- Hardcoded credentials
- Unsafe regex patterns
- Insecure randomness
- HTTP response splitting

## Excluded Paths

The following paths are excluded from analysis to focus on source code:
- `node_modules/` - Dependencies
- `dist/`, `build/` - Build outputs
- `__pycache__/`, `*.pyc` - Python cache files
- `migrations/` - Database migrations
- Documentation files
- Configuration files

## Viewing Results

1. Go to the **Security** tab in the GitHub repository
2. Click **Code scanning alerts** to see CodeQL findings
3. Each alert includes:
   - Detailed vulnerability description
   - Code location and path
   - Severity assessment
   - Remediation guidance

## Integration

CodeQL results are automatically uploaded to GitHub's security dashboard and can be:
- Viewed in the Security tab
- Integrated with branch protection rules
- Used to block PRs with critical vulnerabilities
- Exported via GitHub's API

## Testing

Test files are included to verify CodeQL is working correctly:
- `test_codeql_security.py` - Python security issues for detection
- `frontend/src/test-codeql-security.ts` - TypeScript security issues for detection

These files contain intentional vulnerabilities that CodeQL should flag when the workflow runs.