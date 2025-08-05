# Matrix Testing Setup for RouteForce Routing

This document describes the multi-platform matrix testing implementation for the RouteForce Routing project.

## Overview

The matrix testing setup ensures that RouteForce Routing works correctly across different operating systems and Python versions, providing confidence in cross-platform compatibility.

## Matrix Configuration

### Cross-Platform Testing (`test-cross-platform` job)

Tests core functionality across multiple platforms with unit tests only:

| Platform | Python Versions | Test Type |
|----------|----------------|-----------|
| Ubuntu   | 3.10, 3.11, 3.12 | Unit tests |
| Windows  | 3.11, 3.12 | Unit tests |
| macOS    | 3.10, 3.12 | Unit tests |

**Total combinations:** 7 optimized matrix combinations

### Integration Testing (`test` job)

Full integration tests with external services (PostgreSQL, Redis):

| Platform | Python Versions | Test Type |
|----------|----------------|-----------|
| Ubuntu   | 3.10, 3.11, 3.12 | Full integration tests |

**Note:** Integration tests only run on Ubuntu because GitHub Actions services are only supported on Linux runners.

## Features

### Platform-Specific Optimizations

- **Enhanced caching:** Platform-specific pip cache paths for faster builds
- **Conditional testing:** Database-dependent tests automatically skipped on Windows/macOS
- **Optimized matrix:** Strategic exclusions to balance coverage vs CI cost

### Test Categories

1. **Code Quality Checks** (all platforms):
   - Black formatting validation
   - Flake8 linting
   - MyPy type checking

2. **Unit Tests** (all platforms):
   - Core routing logic
   - ML algorithm functionality
   - Business logic validation

3. **Integration Tests** (Ubuntu only):
   - Database interactions (PostgreSQL)
   - Cache operations (Redis)
   - Full system workflows

### Environment Variables

- `SKIP_DB_TESTS`: Set to "true" on non-Linux platforms to skip database-dependent tests

## CI/CD Integration

### Job Dependencies

```
test-cross-platform ─┐
                     ├─→ build ─→ deploy-staging ─→ deploy-production
test (integration)  ─┘
```

### Summary Reporting

The `test-summary` job provides consolidated results from all matrix testing, showing:
- Overall matrix test status
- Platform-specific results
- Integration test status

## Benefits

1. **Cross-Platform Confidence:** Ensures RouteForce works on developer machines regardless of OS
2. **Version Compatibility:** Tests against Python 3.10-3.12 for broad compatibility
3. **Optimized CI Usage:** Strategic matrix design balances coverage with cost
4. **Early Issue Detection:** Platform-specific issues caught before deployment

## Running Tests Locally

To simulate the matrix testing locally:

```bash
# Ubuntu/Linux (full tests)
python -m pytest tests/ --cov=app

# Windows/macOS simulation (skip DB tests)
SKIP_DB_TESTS=true python -m pytest tests/ -k "not (database or db or postgres or redis)"

# Platform compatibility check
python test_matrix_setup.py
```

## Troubleshooting

### Common Issues

1. **Platform-specific dependency failures:** Check requirements.txt for platform compatibility
2. **Service connection errors:** Only affects Ubuntu integration tests
3. **Import errors:** Ensure all required dependencies are installed

### Debugging

Use the matrix validation script:
```bash
python test_matrix_setup.py
```

This will check:
- Platform information
- Python version compatibility
- Core dependency imports
- RouteForce module functionality

## Future Enhancements

Potential improvements to the matrix testing setup:

- [ ] Add Python 3.13 when available
- [ ] Include ARM64 platform testing
- [ ] Add performance benchmarking across platforms
- [ ] Implement browser testing for frontend components
- [ ] Add memory usage profiling per platform