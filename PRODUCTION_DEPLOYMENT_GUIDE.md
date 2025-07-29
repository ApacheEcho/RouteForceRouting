# 🚀 RouteForce Enhanced System - Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the RouteForce Enhanced System to production environments.

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+) or macOS
- **Python**: 3.9+ (3.11+ recommended)
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 20GB+ available space
- **Network**: High-speed internet for external API calls

### Required Services
- **Database**: PostgreSQL 13+ or MySQL 8.0+
- **Cache**: Redis 6.0+
- **Web Server**: Nginx (recommended) or Apache
- **Process Manager**: Gunicorn + Supervisor or systemd

## Environment Setup

### 1. Clone and Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd RouteForceRouting

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=app
SECRET_KEY=your-super-secret-production-key-change-this

# Database Configuration
DATABASE_URL=postgresql://username:password@host:5432/routeforce_db
SQLALCHEMY_DATABASE_URI=postgresql://username:password@host:5432/routeforce_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=3600

# External API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
OPENWEATHER_API_KEY=your-openweather-api-key
TRAFFIC_API_KEY=your-traffic-api-key

# Security Configuration
SECURITY_PASSWORD_SALT=your-password-salt-change-this
WTF_CSRF_SECRET_KEY=your-csrf-secret-key-change-this

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/routeforce/app.log
```

### 3. Database Setup

```bash
# Initialize database
export FLASK_APP=app
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create initial admin user
python -c "
from app import create_app
from app.auth_system import create_user
app = create_app()
with app.app_context():
    create_user('admin@example.com', 'secure-password', 'admin')
"
```

## Production Configuration

### 1. Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
bind = "127.0.0.1:5000"
workers = 4

worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 2. Nginx Configuration

Create `/etc/nginx/sites-available/routeforce`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.pem;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Static files
    location /static {
        alias /path/to/routeforce/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # WebSocket support
    location /socket.io {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### 3. Systemd Service

Create `/etc/systemd/system/routeforce.service`:

```ini
[Unit]
Description=RouteForce Enhanced System
After=network.target

[Service]
Type=notify
User=routeforce
Group=routeforce
WorkingDirectory=/opt/routeforce
Environment=PATH=/opt/routeforce/.venv/bin
ExecStart=/opt/routeforce/.venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Security Hardening

### 1. Application Security

```bash
# Create dedicated user
sudo useradd -r -s /bin/false routeforce
sudo mkdir -p /opt/routeforce
sudo chown routeforce:routeforce /opt/routeforce

# Set file permissions
sudo chmod 755 /opt/routeforce
sudo chmod 600 /opt/routeforce/.env
```

### 2. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Or iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### 3. SSL/TLS Certificate

```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Logging

### 1. Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-flask-exporter
pip install sentry-sdk

# Configure health checks
curl -f http://localhost:5000/health || exit 1
```

### 2. Log Management

```bash
# Logrotate configuration
sudo tee /etc/logrotate.d/routeforce << EOF
/var/log/routeforce/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 routeforce routeforce
    postrotate
        systemctl reload routeforce
    endscript
}
EOF
```

## Deployment Steps

### 1. Pre-deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring tools configured
- [ ] Backup procedures established
- [ ] Performance testing completed

### 2. Deployment Process

```bash
# 1. Stop the service
sudo systemctl stop routeforce

# 2. Update code
cd /opt/routeforce
git pull origin main

# 3. Update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations
flask db upgrade

# 5. Restart services
sudo systemctl start routeforce
sudo systemctl restart nginx

# 6. Verify deployment
curl -f https://your-domain.com/health
```

### 3. Post-deployment Verification

```bash
# Check service status
sudo systemctl status routeforce
sudo systemctl status nginx

# Check logs
sudo journalctl -u routeforce -f
tail -f /var/log/routeforce/app.log

# Run integration tests
python test_comprehensive_integration.py
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_routes_timestamp ON routes(timestamp);
CREATE INDEX idx_routes_driver_id ON routes(driver_id);
CREATE INDEX idx_insights_route_id ON route_insights(route_id);
```

### 2. Caching Strategy

```python
# Redis caching
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_DEFAULT_TIMEOUT = 300
```

### 3. Resource Limits

```bash
# Set ulimits
echo "routeforce soft nofile 65536" >> /etc/security/limits.conf
echo "routeforce hard nofile 65536" >> /etc/security/limits.conf
```

## Backup and Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump routeforce_db > /backups/routeforce_db_$DATE.sql
find /backups -name "routeforce_db_*.sql" -mtime +7 -delete
```

### 2. Application Backup

```bash
#!/bin/bash
# backup_app.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/routeforce_app_$DATE.tar.gz /opt/routeforce
find /backups -name "routeforce_app_*.tar.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check DATABASE_URL configuration
   - Verify database service is running
   - Check network connectivity

2. **High Memory Usage**
   - Monitor worker processes
   - Adjust Gunicorn worker count
   - Check for memory leaks

3. **Slow API Responses**
   - Enable query logging
   - Add database indexes
   - Implement caching

### Health Checks

```bash
# Application health
curl -f http://localhost:5000/health

# Database health
curl -f http://localhost:5000/api/system/status

# External APIs health
curl -f http://localhost:5000/api/system/external-status
```

## Support and Maintenance

### Regular Maintenance Tasks

- **Daily**: Monitor logs and performance metrics
- **Weekly**: Review security alerts and updates
- **Monthly**: Database maintenance and optimization
- **Quarterly**: Security audit and penetration testing

### Contact Information

- **Development Team**: dev@routeforce.com
- **Operations Team**: ops@routeforce.com
- **Emergency Contact**: +1-555-ROUTE-911

---

**Deployment Guide Version**: 2.0  
**Last Updated**: January 15, 2025  
**Status**: Production Ready ✅
