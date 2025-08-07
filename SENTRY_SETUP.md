# 📊 Sentry Setup Guide for RouteForce Routing

This guide provides comprehensive instructions for setting up Sentry error tracking and performance monitoring in the RouteForce Routing application.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup)
- [Configuration](#configuration)
- [Features](#features)
- [Integration Examples](#integration-examples)
- [Monitoring Dashboards](#monitoring-dashboards)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## 🎯 Overview

Sentry provides comprehensive monitoring for RouteForce Routing with:

- **Error Tracking**: Real-time error capture and alerting
- **Performance Monitoring**: Request/response and algorithm performance tracking
- **Release Management**: Automated release tracking and deployment monitoring
- **Custom Metrics**: Route optimization and API usage analytics
- **Integration**: Seamless Flask, SQLAlchemy, Redis, and Celery integration

## ⚡ Quick Setup

### 1. Install Sentry SDK

```bash
pip install sentry-sdk[flask]
```

### 2. Get Your Sentry DSN

1. Create a new project in [Sentry.io](https://sentry.io)
2. Select "Flask" as your platform
3. Copy your DSN (Data Source Name)

### 3. Configure Environment

```bash
# Copy example configuration
cp .env.sentry.example .env

# Edit .env file with your Sentry DSN
SENTRY_DSN=https://your-dsn@sentry.io/project-id
FLASK_ENV=production
SENTRY_RELEASE=1.0.0
```

### 4. Start Application

```bash
python app.py
```

✅ **That's it!** Sentry monitoring is now active.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SENTRY_DSN` | Your Sentry project DSN | None (required) | `https://abc@sentry.io/123` |
| `FLASK_ENV` | Environment name | `development` | `production` |
| `SENTRY_RELEASE` | Release version | `1.0.0` | `v2.1.3` |
| `SENTRY_TRACES_SAMPLE_RATE` | Performance monitoring sample rate | `0.1` | `0.2` |
| `SENTRY_PROFILES_SAMPLE_RATE` | Profiling sample rate | `0.1` | `0.1` |

### Advanced Configuration

```python
# app/monitoring/sentry_config.py
class SentryConfig:
    def __init__(self):
        self.dsn = os.environ.get('SENTRY_DSN')
        self.environment = os.environ.get('FLASK_ENV', 'development')
        self.release = os.environ.get('SENTRY_RELEASE', '1.0.0')
        
        # Performance monitoring rates (0.0 to 1.0)
        self.traces_sample_rate = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))
        self.profiles_sample_rate = float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1'))
```

## 🚀 Features

### 1. **Error Tracking**

**Automatic Error Capture:**
- All unhandled exceptions are automatically captured
- Stack traces with local variables
- Request context (URL, method, headers, user)
- Custom error filtering and grouping

**Example:**
```python
# Errors are automatically captured
def risky_function():
    result = 1 / 0  # This will be sent to Sentry
```

### 2. **Performance Monitoring**

**Request Performance:**
- HTTP request/response timing
- Database query performance
- API endpoint monitoring
- Slow request detection

**Algorithm Performance:**
```python
from app.monitoring import monitor_performance

@monitor_performance("genetic_algorithm")
def optimize_route(locations):
    # Performance is automatically tracked
    return optimized_route
```

### 3. **Custom Metrics**

**Route Optimization Metrics:**
```python
from app.monitoring import SentryHelper

# Capture algorithm performance
SentryHelper.capture_performance_metrics(
    algorithm_type="genetic_algorithm",
    execution_time=2.5,
    memory_usage_mb=128,
    location_count=50
)
```

**API Usage Tracking:**
```python
# Track API endpoint usage
SentryHelper.capture_api_usage(
    endpoint="/api/optimize",
    response_time=1.2,
    status_code=200,
    user_id="user_123"
)
```

### 4. **Context Management**

**Scoped Context:**
```python
from app.monitoring import SentryContext

with SentryContext("route_calculation", algorithm="dijkstra") as ctx:
    ctx.set_context("locations", {"count": len(locations)})
    result = calculate_route(locations)
    ctx.add_breadcrumb("Route calculated successfully")
```

## 💡 Integration Examples

### 1. **Route Optimization Monitoring**

```python
from app.monitoring.route_optimization_monitoring import SentryGeneticAlgorithmOptimizer

# Initialize optimizer with built-in monitoring
optimizer = SentryGeneticAlgorithmOptimizer()

# Optimize with comprehensive tracking
result = optimizer.optimize(locations, constraints)
```

### 2. **Flask Route Integration**

```python
from flask import Flask, request, jsonify
from app.monitoring import SentryHelper
import time

@app.route('/api/optimize', methods=['POST'])
def optimize_route():
    start_time = time.time()
    
    try:
        # Your optimization logic here
        result = perform_optimization()
        
        # Track successful API usage
        response_time = time.time() - start_time
        SentryHelper.capture_api_usage(
            '/api/optimize',
            response_time,
            200,
            request.headers.get('X-User-ID')
        )
        
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        # Error is automatically captured by Sentry
        response_time = time.time() - start_time
        SentryHelper.capture_api_usage(
            '/api/optimize',
            response_time,
            500,
            request.headers.get('X-User-ID')
        )
        raise
```

### 3. **Database Error Monitoring**

```python
from app.monitoring import SentryHelper

try:
    db.session.execute(query)
    db.session.commit()
except Exception as e:
    SentryHelper.capture_database_error(
        operation="INSERT",
        table="routes",
        error=e,
        query=str(query)
    )
    raise
```

## 📊 Monitoring Dashboards

### 1. **Issues Dashboard**
- Real-time error tracking
- Error frequency and trends
- Stack traces and context
- User impact analysis

**Access:** `https://sentry.io/organizations/your-org/issues/`

### 2. **Performance Dashboard**
- Request/response timing
- Database query performance
- Algorithm execution times
- Performance trends

**Access:** `https://sentry.io/organizations/your-org/performance/`

### 3. **Releases Dashboard**
- Deployment tracking
- Release health
- Issue assignment to releases
- Performance regressions

**Access:** `https://sentry.io/organizations/your-org/releases/`

## 🔧 GitHub Actions Integration

### Automated Release Management

The included GitHub Actions workflow automatically:

1. **Creates Sentry releases** on every push to main/develop
2. **Uploads source maps** for better error tracking
3. **Sets commit information** for release tracking
4. **Creates deployments** for environment tracking

### Setup Steps

1. **Add Sentry Auth Token to GitHub Secrets:**
   ```bash
   # Get token from https://sentry.io/settings/auth-tokens/
   gh secret set SENTRY_AUTH_TOKEN
   ```

2. **Add Sentry DSN to GitHub Secrets:**
   ```bash
   gh secret set SENTRY_DSN
   ```

3. **Configure organization and project in workflow:**
   ```yaml
   env:
     SENTRY_ORG: your-organization
     SENTRY_PROJECT: your-project
   ```

## 🚨 Troubleshooting

### Common Issues

**1. "No DSN configured" Error**
```bash
# Solution: Set SENTRY_DSN environment variable
export SENTRY_DSN="https://your-dsn@sentry.io/project-id"
```

**2. High Noise Levels**
```python
# Solution: Adjust sample rates in configuration
SENTRY_TRACES_SAMPLE_RATE=0.05  # Lower sample rate
```

**3. Missing Performance Data**
```python
# Solution: Enable performance monitoring
enable_tracing=True
traces_sample_rate=0.1
```

**4. Releases Not Appearing**
```bash
# Solution: Verify auth token has releases:write scope
# Check token at https://sentry.io/settings/auth-tokens/
```

### Debug Mode

Enable debug logging to troubleshoot Sentry integration:

```python
import logging
logging.getLogger('sentry_sdk').setLevel(logging.DEBUG)
```

### Testing Integration

```python
# Test Sentry integration locally
from app.monitoring.sentry_config import init_sentry
import sentry_sdk

# Initialize Sentry
init_sentry()

# Send test error
sentry_sdk.capture_message("Test message from RouteForce Routing!", level="info")

# Trigger test error
try:
    1 / 0
except Exception as e:
    sentry_sdk.capture_exception(e)
```

## 🎯 Best Practices

### 1. **Error Filtering**

```python
# Filter out non-critical errors
def before_send_filter(event, hint):
    # Skip 404 errors in production
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if hasattr(exc_value, 'code') and exc_value.code == 404:
            return None
    return event
```

### 2. **Performance Sampling**

```python
# Use appropriate sample rates for your traffic
SENTRY_TRACES_SAMPLE_RATE=0.1   # 10% of transactions (recommended for high traffic)
SENTRY_TRACES_SAMPLE_RATE=1.0   # 100% of transactions (for development/low traffic)
```

### 3. **Context Management**

```python
# Add relevant context to help debugging
with SentryContext("optimization", algorithm="genetic") as ctx:
    ctx.set_context("input", {
        "location_count": len(locations),
        "constraints": constraints,
        "user_preferences": user_prefs
    })
    result = optimize(locations)
```

### 4. **User Privacy**

```python
# Configure Sentry to respect user privacy
sentry_sdk.init(
    send_default_pii=False,  # Don't send personally identifiable information
    before_send=scrub_sensitive_data
)
```

### 5. **Release Management**

```bash
# Use semantic versioning for releases
SENTRY_RELEASE=v1.2.3

# Or use git commit hash for development
SENTRY_RELEASE=$(git rev-parse --short HEAD)
```

## 📈 Monitoring Strategy

### 1. **Development**
- Full sampling (100%) for complete visibility
- Capture all errors for immediate debugging
- Monitor algorithm performance during testing

### 2. **Staging**
- Medium sampling (20%) for realistic performance testing
- Test release management and deployment tracking
- Validate error grouping and filtering

### 3. **Production**
- Conservative sampling (5-10%) to manage costs
- Focus on critical errors and performance issues
- Set up alerts for high-severity issues

## 🔗 Additional Resources

- **Sentry Documentation**: https://docs.sentry.io/platforms/python/guides/flask/
- **Flask Integration Guide**: https://docs.sentry.io/platforms/python/guides/flask/
- **Performance Monitoring**: https://docs.sentry.io/product/performance/
- **Release Management**: https://docs.sentry.io/product/releases/

---

*This setup guide is maintained as part of the RouteForce Routing project. For questions or improvements, please create an issue in the repository.*
