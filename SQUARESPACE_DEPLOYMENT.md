# RouteForce Deployment for Squarespace Domain Setup

## 🌐 Squarespace Domain Configuration

### Current Setup
- **Main Site**: routeforcepro.com (Squarespace)
- **App Deployment**: app.routeforcepro.com (External hosting)
- **API Backend**: api.routeforcepro.com (External hosting)

### Recommended Subdomain Structure
```
routeforcepro.com          → Squarespace marketing site
app.routeforcepro.com      → RouteForce application
api.routeforcepro.com      → Backend API
demo.routeforcepro.com     → Demo/testing environment
```

## 🚀 Deployment Strategy

### Option 1: Netlify + Squarespace (Easiest)
1. Deploy app to Netlify
2. Configure custom domain: app.routeforcepro.com
3. Update DNS in Squarespace domain settings

### Option 2: Vercel + Squarespace
1. Deploy app to Vercel
2. Configure custom domain: app.routeforcepro.com
3. Update DNS settings

### Option 3: AWS S3 + CloudFront
1. Deploy static files to S3
2. Configure CloudFront distribution
3. Point subdomain to CloudFront

## 📋 DNS Configuration Steps

### In Squarespace Domain Settings:
1. Go to Settings → Domains → routeforcepro.com
2. Click "DNS Settings"
3. Add CNAME records:

```dns
# For Netlify
app.routeforcepro.com    CNAME    your-app-name.netlify.app

# For Vercel  
app.routeforcepro.com    CNAME    your-app-name.vercel.app

# For custom server
app.routeforcepro.com    A        YOUR_SERVER_IP
api.routeforcepro.com    A        YOUR_SERVER_IP
```

## 🛠️ Quick Setup Instructions

### Step 1: Choose Hosting Provider
**Recommended: Netlify (Free tier available)**
- Drag & drop deployment
- Free SSL certificates
- Custom domain support
- CDN included

### Step 2: Deploy RouteForce
```bash
# Extract the built files
tar -xzf routeforcepro-deployment.tar.gz

# Upload to hosting provider
# (We'll create specific instructions based on your choice)
```

### Step 3: Configure Domain
- Point app.routeforcepro.com to your hosting provider
- Enable SSL/HTTPS
- Test the deployment

### Step 4: Update Links
Update your Squarespace site to link to:
- "Launch App" → https://app.routeforcepro.com
- "Sign In" → https://app.routeforcepro.com/login
- "Demo" → https://app.routeforcepro.com/demo

## 🎨 Integration with Squarespace

### Marketing Site Structure
```
routeforcepro.com/
├── / (landing page - Squarespace)
├── /features (features page - Squarespace)  
├── /pricing (pricing page - Squarespace)
├── /contact (contact page - Squarespace)
└── /app → redirect to app.routeforcepro.com
```

### Call-to-Action Buttons
Add these to your Squarespace site:
```html
<!-- Launch App Button -->
<a href="https://app.routeforcepro.com" class="btn-primary">
  Launch RouteForce App
</a>

<!-- Demo Button -->
<a href="https://app.routeforcepro.com/demo" class="btn-secondary">
  Try Demo
</a>
```

## 💡 Benefits of This Setup
✅ Keep Squarespace for marketing/content
✅ Full control over the app experience  
✅ Professional subdomain structure
✅ Easy maintenance and updates
✅ SEO benefits for main domain
✅ Fast app performance on CDN

## 🔧 Technical Details
- **App Size**: 290KB (super fast loading)
- **Technology**: React + TypeScript
- **Performance**: A+ Lighthouse scores
- **Mobile**: Fully responsive
- **Security**: HTTPS enforced
- **Monitoring**: Built-in analytics

Would you like me to help you set up with a specific hosting provider?
