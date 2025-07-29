#!/bin/bash
# SSL Certificate Setup with Certbot and NGINX

echo "🔐 Setting up SSL certificates for RouteForce..."

# Create NGINX configuration for RouteForce
echo "📝 Creating NGINX configuration..."

cat << 'EOF' | sudo tee /etc/nginx/sites-available/routeforce
# RouteForce NGINX Configuration
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name app.routeforcepro.com;
    return 301 https://$host$request_uri;
}

# HTTPS server configuration
server {
    listen 443 ssl http2;
    server_name app.routeforcepro.com;

    # SSL Certificate paths (will be set by Certbot)
    ssl_certificate /etc/letsencrypt/live/app.routeforcepro.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.routeforcepro.com/privkey.pem;

    # SSL Security Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Client max body size for file uploads
    client_max_body_size 16M;

    # Proxy configuration for Flask backend
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static file serving optimization
    location /static/ {
        alias /home/deploy/routeforce/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

echo "✅ NGINX configuration created"

# Install Certbot (Ubuntu/Debian)
echo "📦 Installing Certbot..."
if command -v apt >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y certbot python3-certbot-nginx
elif command -v brew >/dev/null 2>&1; then
    echo "📝 On macOS, install with: brew install certbot"
    echo "💡 For production, run this on your Linux server"
fi

# Enable NGINX configuration
echo "🔧 Enabling NGINX configuration..."
sudo ln -sf /etc/nginx/sites-available/routeforce /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Generate SSL certificate
echo "🔐 Generating SSL certificate..."
echo "💡 Run this command on your production server:"
echo "sudo certbot --nginx -d app.routeforcepro.com"

# Set up auto-renewal
echo "🔄 Setting up certificate auto-renewal..."
echo "💡 Test auto-renewal with:"
echo "sudo certbot renew --dry-run"

# Create renewal cron job
cat << 'EOF' > /tmp/certbot-renewal
#!/bin/bash
# Certbot renewal script
/usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

echo "📅 Add this to crontab for auto-renewal:"
echo "0 12 * * * /tmp/certbot-renewal"

echo "✅ SSL setup script complete!"
echo "🚀 Your site will be available at: https://app.routeforcepro.com"
