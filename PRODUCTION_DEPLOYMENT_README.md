# 🚀 RouteForce Production Deployment Guide

## Overview
Complete production deployment setup for RouteForce with PostgreSQL, SSL, and CI/CD.

## 📋 Prerequisites
- Ubuntu/Debian server with root access
- Domain name pointing to your server (app.routeforcepro.com)
- GitHub repository with Actions enabled

## 🏗️ Architecture
```
Internet → NGINX (SSL) → Gunicorn → Flask App → PostgreSQL
                      → Redis (optional)
```

## 📦 Quick Setup

### 1. Server Preparation
```bash
# Create deploy user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG sudo deploy

# Switch to deploy user
sudo su - deploy

# Clone repository
git clone https://github.com/your-username/RouteForceRouting.git
cd RouteForceRouting
```

### 2. Run Automated Setup
```bash
# Run the complete setup script
chmod +x scripts/production_setup.sh
./scripts/production_setup.sh
```

### 3. Manual SSL Setup
```bash
# Get SSL certificate
sudo certbot --nginx -d app.routeforcepro.com
```

### 4. Configure GitHub Secrets
Add these secrets to your GitHub repository:
- `PROD_HOST`: Your server IP/domain
- `PROD_USER`: deploy
- `SSH_PRIVATE_KEY`: Your SSH private key
- `DATABASE_URL`: PostgreSQL connection string

## 🔧 Individual Setup Steps

### PostgreSQL Setup
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createdb routeforce_prod
sudo -u postgres createuser -P routeforce_user

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE routeforce_prod TO routeforce_user;"
```

### SSL Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Copy NGINX configuration
sudo cp nginx/routeforce.conf /etc/nginx/sites-available/routeforce
sudo ln -s /etc/nginx/sites-available/routeforce /etc/nginx/sites-enabled/

# Get certificate
sudo certbot --nginx -d app.routeforcepro.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Application Service
```bash
# Copy and enable systemd service
sudo cp scripts/routeforce.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable routeforce
sudo systemctl start routeforce
```

## 🚀 CI/CD Pipeline
The GitHub Actions workflow automatically:
1. Runs tests on every push to main
2. Builds the React frontend
3. Deploys to production server via SSH
4. Restarts services
5. Performs health checks

## 📊 Monitoring

### Service Status
```bash
# Check application status
sudo systemctl status routeforce

# View logs
sudo journalctl -f -u routeforce

# Check NGINX status
sudo systemctl status nginx
```

### Health Checks
- Application: `https://app.routeforcepro.com/health`
- API: `https://app.routeforcepro.com/api/health`

## 🔐 Security Features
- SSL/TLS encryption with Let's Encrypt
- Security headers (HSTS, X-Frame-Options, etc.)
- Rate limiting via Flask-Limiter
- CORS configuration
- JWT authentication
- Database connection pooling

## 🛠️ Troubleshooting

### Common Issues
1. **502 Bad Gateway**: Check if Flask app is running
   ```bash
   sudo systemctl restart routeforce
   ```

2. **Database Connection Error**: Check PostgreSQL service
   ```bash
   sudo systemctl status postgresql
   ```

3. **SSL Certificate Issues**: Renew certificate
   ```bash
   sudo certbot renew
   ```

### Log Locations
- Application: `sudo journalctl -u routeforce`
- NGINX: `/var/log/nginx/error.log`
- PostgreSQL: `/var/log/postgresql/`

## 🔄 Updates and Maintenance

### Manual Deployment
```bash
cd /home/deploy/routeforce
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm run build && cd ..
sudo systemctl restart routeforce
```

### Database Backup
```bash
# Create backup
sudo -u postgres pg_dump routeforce_prod > backup_$(date +%Y%m%d).sql

# Restore backup
sudo -u postgres psql routeforce_prod < backup_20250122.sql
```

## 📈 Performance Optimization
- Gunicorn with 4 workers
- NGINX gzip compression
- Static file caching
- Database connection pooling
- Redis caching (optional)

## ✅ Final Result
- ✅ Secure HTTPS site at app.routeforcepro.com
- ✅ Production-grade PostgreSQL backend
- ✅ Automated CI/CD pipeline
- ✅ Health monitoring and logging
- ✅ SSL auto-renewal
- ✅ Enterprise security features

## 📞 Support
For deployment issues:
1. Check logs: `sudo journalctl -f -u routeforce`
2. Verify configuration: `nginx -t`
3. Test database: `sudo -u postgres psql routeforce_prod -c "\dt"`
4. Check GitHub Actions for CI/CD issues
