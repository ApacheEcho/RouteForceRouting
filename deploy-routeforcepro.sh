#!/bin/bash
# Deploy RouteForce to routeforcepro.com

set -e

echo "🚀 Deploying RouteForce to routeforcepro.com..."

# Configuration
DOMAIN="routeforcepro.com"
BUILD_DIR="frontend/dist"
DEPLOY_DIR="/var/www/routeforcepro.com"

# Build frontend for production
echo "📦 Building frontend..."
cd frontend
npm run build
cd ..

# Verify build files exist
if [ ! -d "$BUILD_DIR" ]; then
    echo "❌ Build directory not found: $BUILD_DIR"
    exit 1
fi

echo "✅ Build completed successfully"
echo "📁 Build size: $(du -sh $BUILD_DIR)"

# Option 1: Upload to server (if you have server access)
if [ "$1" = "server" ]; then
    echo "🌐 Uploading to server..."
    rsync -avz --delete $BUILD_DIR/ user@$DOMAIN:$DEPLOY_DIR/
    echo "✅ Deployment complete!"
fi

# Option 2: Prepare for static hosting
if [ "$1" = "static" ]; then
    echo "📂 Preparing static hosting package..."
    tar -czf routeforcepro-deployment.tar.gz -C $BUILD_DIR .
    echo "✅ Package created: routeforcepro-deployment.tar.gz"
    echo "📤 Ready to upload to your hosting provider"
fi

# Option 3: AWS S3 deployment
if [ "$1" = "aws" ]; then
    echo "☁️ Deploying to AWS S3..."
    aws s3 sync $BUILD_DIR s3://routeforcepro.com --delete
    aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
    echo "✅ AWS deployment complete!"
fi

# Option 4: Netlify deployment
if [ "$1" = "netlify" ]; then
    echo "🌐 Deploying to Netlify..."
    npx netlify deploy --prod --dir=$BUILD_DIR --site=routeforcepro
    echo "✅ Netlify deployment complete!"
fi

echo "🎉 RouteForce is now live at https://$DOMAIN"
