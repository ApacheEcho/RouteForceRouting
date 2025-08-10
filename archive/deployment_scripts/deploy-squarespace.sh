#!/bin/bash
# Quick deploy RouteForce to work with Squarespace domain

echo "🚀 Preparing RouteForce for Squarespace Integration"
echo "Domain: routeforcepro.com (Squarespace) + app.routeforcepro.com (RouteForce)"

# Build the app
echo "📦 Building production app..."
cd frontend
npm run build
cd ..

# Create deployment package
echo "📦 Creating deployment package..."
rm -f routeforce-squarespace.zip
cd frontend/dist
zip -r ../../routeforce-squarespace.zip ./*
cd ../..

echo "✅ Deployment package ready: routeforce-squarespace.zip"
echo ""
echo "🌐 Next Steps for Squarespace Integration:"
echo ""
echo "1. 📁 Upload routeforce-squarespace.zip to Netlify:"
echo "   - Go to https://app.netlify.com"
echo "   - Drag & drop the zip file"
echo "   - Your site will be live at: https://random-name.netlify.app"
echo ""
echo "2. 🔧 Configure custom domain in Netlify:"
echo "   - Site settings → Domain management"
echo "   - Add custom domain: app.routeforcepro.com"
echo "   - Copy the DNS settings shown"
echo ""
echo "3. 🌐 Update DNS in Squarespace:"
echo "   - Settings → Domains → routeforcepro.com → DNS Settings"
echo "   - Add CNAME record: app → your-site.netlify.app"
echo ""
echo "4. 🔗 Update your Squarespace site:"
echo "   - Add button/link: 'Launch App' → https://app.routeforcepro.com"
echo ""
echo "🎉 Your RouteForce app will be live at: https://app.routeforcepro.com"
echo "📊 Size: $(du -sh frontend/dist | cut -f1) - Super fast loading!"
