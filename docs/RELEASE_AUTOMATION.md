# Release Automation Documentation

This document describes the automated release process for the RouteForce Routing project.

## Overview

The release automation system provides a seamless way to create versioned releases with automatically generated changelogs. It integrates with the existing CI/CD pipeline to ensure quality and consistency.

## 🚀 Quick Start

### Creating a Release

1. **Using the helper script (Recommended):**
   ```bash
   ./scripts/release.sh 1.0.0
   ```

2. **Manual process:**
   ```bash
   # Update version
   echo "1.0.0" > VERSION
   
   # Create and push tag
   git add VERSION
   git commit -m "Bump version to 1.0.0"
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

3. **Via GitHub UI:**
   - Go to Actions → Release Automation
   - Click "Run workflow"
   - Enter the version (e.g., v1.0.0)

## 📋 Release Process

### Automatic Workflow

When a tag is pushed (format: `v*.*.*`), the following happens automatically:

1. **Validation & Testing**
   - Code quality checks (Black, Flake8)
   - Application tests with PostgreSQL and Redis
   - Import validation

2. **Build Assets**
   - Source distribution
   - Deployment package (.tar.gz)
   - Updates version in files

3. **Generate Changelog**
   - Extracts commits since last release
   - Updates CHANGELOG.md
   - Creates formatted release notes

4. **Create GitHub Release**
   - Publishes release with assets
   - Includes auto-generated changelog
   - Marks pre-releases appropriately

5. **Post-Release**
   - Commits updated CHANGELOG.md
   - Triggers deployment for stable releases

### Release Types

- **Stable Release:** `v1.0.0` - Production-ready
- **Pre-release:** `v1.0.0-beta.1` - Testing/preview version
- **Release Candidate:** `v1.0.0-rc.1` - Final testing before stable

## 🛠️ Tools and Scripts

### Release Helper Script

Location: `scripts/release.sh`

**Features:**
- Version format validation
- Git tag conflict checking
- Interactive confirmation
- Dry-run mode
- Force mode for automation

**Usage Examples:**
```bash
# Create a stable release
./scripts/release.sh 1.0.0

# Create a pre-release
./scripts/release.sh 1.1.0-beta.1

# Preview without changes
./scripts/release.sh --dry-run 2.0.0

# Skip confirmations (for CI)
./scripts/release.sh --force 1.0.1

# Show help
./scripts/release.sh --help
```

### Version Management

**Version File:** `VERSION`
- Contains current version number
- Used by build processes
- Updated automatically by release script

**Semantic Versioning:** Following [SemVer](https://semver.org/)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

## 📝 Changelog

### Format

Following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.0.0] - 2024-01-15

### Added
- New features

### Changed  
- Modified features

### Fixed
- Bug fixes

### Removed
- Deleted features
```

### Automatic Generation

The system automatically:
- Extracts commit messages since last release
- Formats them into changelog entries
- Updates CHANGELOG.md
- Includes installation instructions
- Adds comparison links

## 🔧 Configuration

### Workflow Permissions

Required permissions in `.github/workflows/release.yml`:
```yaml
permissions:
  contents: write      # Create releases and tags
  packages: write      # Publish packages
  pull-requests: write # Update PRs
```

### Environment Variables

**Build Environment:**
- `PYTHON_VERSION`: Python version for builds (default: 3.12)
- `FLASK_ENV`: Set to 'testing' for test runs

**Database Services:**
- PostgreSQL 16 for testing
- Redis 7 for caching tests

### Secrets

No additional secrets required beyond `GITHUB_TOKEN` (automatically provided).

## 🔗 Integration with CI/CD

### Existing Workflows

The release automation integrates with:
- **ci-cd.yml**: Main CI/CD pipeline
- **test.yml**: Test execution
- **deploy.yml**: Production deployment

### Triggering Deployments

Stable releases automatically trigger:
- Production deployment (non-pre-releases)
- Notification systems
- Package registrations

## 📦 Release Assets

Each release includes:

1. **Source Package** (`routeforce-v*.tar.gz`)
   - Complete application code
   - Configuration files
   - Documentation
   - Deployment scripts

2. **Release Notes**
   - Change summary
   - Installation instructions
   - Upgrade notes

## 🚨 Troubleshooting

### Common Issues

**"Tag already exists"**
```bash
# Check existing tags
git tag --list | sort -V

# Delete local tag if needed
git tag -d v1.0.0

# Delete remote tag if needed
git push origin --delete v1.0.0
```

**"Workflow failed on tests"**
- Check GitHub Actions logs
- Verify code quality issues
- Ensure tests pass locally

**"Permission denied"**
- Verify repository permissions
- Check workflow permissions
- Ensure GITHUB_TOKEN is available

### Manual Recovery

If automation fails:

1. **Delete the problematic tag:**
   ```bash
   git tag -d v1.0.0
   git push origin --delete v1.0.0
   ```

2. **Fix the issue and retry:**
   ```bash
   # Fix code/tests
   git add .
   git commit -m "Fix release issues"
   
   # Recreate release
   ./scripts/release.sh 1.0.0
   ```

## 📊 Monitoring

### Release Status

Monitor releases at:
- **Actions:** https://github.com/ApacheEcho/RouteForceRouting/actions
- **Releases:** https://github.com/ApacheEcho/RouteForceRouting/releases

### Quality Gates

Each release must pass:
- ✅ Code formatting (Black)
- ✅ Linting (Flake8)
- ✅ Application imports
- ✅ Test execution
- ✅ Build process

## 📚 Best Practices

### Before Release

1. **Update documentation**
2. **Run tests locally**
3. **Review recent commits**
4. **Plan version number**

### Version Strategy

- **Patch releases:** Bug fixes, minor improvements
- **Minor releases:** New features, enhancements
- **Major releases:** Breaking changes, architecture updates
- **Pre-releases:** Testing new features

### Commit Messages

Use clear, descriptive commit messages:
- `feat: add new routing algorithm`
- `fix: resolve geocoding cache issue`
- `docs: update API documentation`
- `refactor: improve database connections`

## 🔄 Maintenance

### Regular Tasks

- **Review CHANGELOG.md** for accuracy
- **Update release documentation** as needed
- **Monitor workflow performance**
- **Archive old releases** if needed

### Workflow Updates

When updating the release workflow:
1. Test in a fork first
2. Use dry-run mode
3. Update documentation
4. Monitor first few releases

---

For questions or issues with the release process, please:
1. Check this documentation
2. Review recent releases for examples  
3. Open an issue with "release:" label