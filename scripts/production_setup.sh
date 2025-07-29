#!/bin/bash
# Complete Production Deployment Setup for RouteForce

echo "🚀 RouteForce Production Deployment Stack Setup"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Don't run this script as root. Create a deploy user first."
   exit 1
fi

echo "1️⃣ Setting up PostgreSQL..."
echo "----------------------------"

# Install PostgreSQL (Ubuntu/Debian)
if command -v apt >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE routeforce_prod;
CREATE USER routeforce_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE routeforce_prod TO routeforce_user;
\c routeforce_prod
GRANT ALL ON SCHEMA public TO routeforce_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO routeforce_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO routeforce_user;
\q
EOF
    
    echo "✅ PostgreSQL database created"
fi

echo ""
echo "2️⃣ Setting up SSL with Certbot..."
echo "---------------------------------"

# Install NGINX and Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Copy NGINX configuration
sudo cp scripts/routeforce.nginx /etc/nginx/sites-available/routeforce
sudo ln -sf /etc/nginx/sites-available/routeforce /etc/nginx/sites-enabled/

# Test NGINX configuration
sudo nginx -t

# Start NGINX
sudo systemctl start nginx
sudo systemctl enable nginx

echo "💡 Run this command to get SSL certificate:"
echo "sudo certbot --nginx -d app.routeforcepro.com"

echo ""
echo "3️⃣ Setting up Application Service..."
echo "------------------------------------"

# Copy systemd service file
sudo cp scripts/routeforce.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable routeforce

echo "✅ System service configured"

echo ""
echo "4️⃣ Setting up GitHub Actions Secrets..."
echo "---------------------------------------"

echo "Add these secrets to your GitHub repository:"
echo "PROD_HOST=your_server_ip_or_domain"
echo "PROD_USER=deploy"
echo "SSH_PRIVATE_KEY=your_ssh_private_key"
echo "DATABASE_URL=postgresql://routeforce_user:your_secure_password_here@localhost:5432/routeforce_prod"

echo ""
echo "5️⃣ Initial Application Deployment..."
echo "------------------------------------"

# Create application directory
mkdir -p /home/deploy/routeforce
cd /home/deploy/routeforce

# Clone repository (if not already done)
if [ ! -d ".git" ]; then
    git clone https://github.com/your-username/RouteForceRouting.git .
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Set up environment file
cp .env.production.template .env.production
echo "💡 Edit .env.production with your actual configuration"

# Initialize database
export DATABASE_URL="postgresql://routeforce_user:your_secure_password_here@localhost:5432/routeforce_prod"
python -c "
from app import create_app
from app.models.database import db
app = create_app('production')
with app.app_context():
    db.create_all()
print('✅ Database initialized')
"

# Start the service
sudo systemctl start routeforce

echo ""
echo "🏁 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "✅ PostgreSQL database: routeforce_prod"
echo "✅ SSL ready for: app.routeforcepro.com"
echo "✅ NGINX reverse proxy configured"
echo "✅ Systemd service: routeforce"
echo "✅ GitHub Actions CI/CD pipeline ready"
echo ""
echo "Next steps:"
echo "1. Run: sudo certbot --nginx -d app.routeforcepro.com"
echo "2. Configure GitHub repository secrets"
echo "3. Push to main branch to trigger deployment"
echo "4. Access your site: https://app.routeforcepro.com"
echo ""
echo "🔧 Useful commands:"
echo "sudo systemctl status routeforce    # Check service status"
echo "sudo journalctl -f -u routeforce   # View service logs"
echo "sudo systemctl reload nginx        # Reload NGINX"
echo "sudo certbot renew --dry-run       # Test SSL renewal"
