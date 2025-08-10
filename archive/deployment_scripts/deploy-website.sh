#!/bin/bash
# RouteForce Website Deployment Script

set -e

echo "🚀 RouteForce Website Deployment Starting..."

# Build the frontend
echo "📦 Building React frontend..."
cd frontend
npm install
npm run build

# Create deployment directory
echo "📁 Preparing deployment files..."
cd ..
rm -rf deploy/
mkdir -p deploy/website

# Copy frontend build to deployment
cp -r frontend/dist/* deploy/website/

# Copy backend files for server deployment
mkdir -p deploy/backend
cp -r app/ deploy/backend/
cp -r requirements.txt deploy/backend/
cp -r *.py deploy/backend/
cp -r Dockerfile.production deploy/backend/Dockerfile

# Create production configuration
cat > deploy/website/.htaccess << 'EOF'
# RouteForce Frontend Configuration
RewriteEngine On

# Handle React Router
RewriteBase /
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>
EOF

# Create nginx configuration
cat > deploy/nginx.conf << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name routeforce.com www.routeforce.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name routeforce.com www.routeforce.com;

    # SSL Configuration (replace with your certificates)
    ssl_certificate /etc/ssl/certs/routeforce.crt;
    ssl_certificate_key /etc/ssl/private/routeforce.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # Frontend
    location / {
        root /var/www/routeforce;
        try_files $uri $uri/ /index.html;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }
}
EOF

# Create Docker deployment
cat > deploy/docker-compose.website.yml << 'EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./website:/var/www/routeforce
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - /etc/ssl/certs:/etc/ssl/certs:ro
      - /etc/ssl/private:/etc/ssl/private:ro
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/routeforce
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=routeforce
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Create Netlify/Vercel deployment config
cat > deploy/website/_redirects << 'EOF'
# Netlify redirects for React Router
/*    /index.html   200

# API proxy to backend
/api/*  https://api.routeforce.com/api/:splat  200
/health https://api.routeforce.com/health  200
/metrics https://api.routeforce.com/metrics  200
EOF

# Create Vercel configuration
cat > deploy/website/vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "." }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.routeforce.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
EOF

echo "✅ Deployment files ready!"
echo ""
echo "📁 Deployment structure:"
echo "   deploy/"
echo "   ├── website/           (Frontend files ready for hosting)"
echo "   ├── backend/           (Backend files for server deployment)"
echo "   ├── nginx.conf         (Nginx configuration)"
echo "   ├── docker-compose.website.yml  (Docker deployment)"
echo "   └── website/"
echo "       ├── _redirects     (Netlify configuration)"
echo "       └── vercel.json    (Vercel configuration)"
echo ""
echo "🚀 Deployment options:"
echo "   1. Static hosting: Upload 'deploy/website/' to any web host"
echo "   2. Netlify: Connect to GitHub and deploy automatically"
echo "   3. Vercel: Deploy with 'vercel --prod'"
echo "   4. VPS/Server: Use nginx.conf and docker-compose.website.yml"
echo ""
