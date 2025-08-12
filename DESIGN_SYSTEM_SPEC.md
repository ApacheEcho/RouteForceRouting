# RouteForce Pro UI - Complete Design System Specification

> **Developer-Ready Design System** - Complete UI Specification  
> All specifications needed to build RouteForce Pro UI components and pages

## 🎨 **Design Tokens**

### **Colors**
```css
:root {
  /* Primary Brand */
  --color-primary: #682C82;
  
  /* Neutrals */
  --color-black: #000000;
  --color-white: #FFFFFF;
  --color-gray-light: #F5F5F5;
  --color-gray-dark: #4A4A4A;
}
```

### **Typography**
```css
:root {
  --font-family: 'Nimbus Sans Bold', -apple-system, BlinkMacSystemFont, sans-serif;
  
  /* Heading Styles */
  --text-h1: bold 48px/1.2 var(--font-family);
  --text-h2: bold 36px/1.3 var(--font-family);
  --text-h3: bold 28px/1.4 var(--font-family);
  
  /* Body Styles */
  --text-body: normal 16px/1.5 var(--font-family);
  --text-body-small: normal 14px/1.4 var(--font-family);
}
```

### **Spacing Scale**
```css
:root {
  --space-xs: 8px;
  --space-sm: 16px;
  --space-md: 24px;
  --space-lg: 32px;
  --space-xl: 48px;
  --space-2xl: 64px;
}
```

---

## 🧩 **Component Specifications**

### **1. Header Navigation**
**Structure:** Logo + Navigation Menu + CTA Button

```html
<header class="header-nav">
  <div class="logo-slot">
    <!-- RouteForce Logo -->
  </div>
  <nav class="nav-links">
    <a href="/dashboard">Dashboard</a>
    <a href="/routes">Route Generator</a>
    <a href="/features">Features</a>
  </nav>
  <button class="cta-button primary">Get Started</button>
</header>
```

**Styles:**
- Background: `var(--color-white)`
- Padding: `var(--space-sm) var(--space-lg)`
- Border-bottom: `1px solid var(--color-gray-light)`
- Logo: 120px width
- Nav links: `var(--text-body)`, `var(--color-gray-dark)`
- CTA Button: Primary button style (see below)

### **2. Primary Button**
**States:** Default, Hover, Disabled

```html
<button class="btn btn-primary">
  Button Text
</button>
```

**Styles:**
```css
.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
  padding: var(--space-sm) var(--space-lg);
  border: none;
  border-radius: 8px;
  font: var(--text-body);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #5a2470; /* Darker primary */
  transform: translateY(-1px);
}

.btn-primary:disabled {
  background: var(--color-gray-light);
  color: var(--color-gray-dark);
  cursor: not-allowed;
}
```

### **3. Feature Card**
**Structure:** Icon + Headline + Description + Optional Link

```html
<div class="feature-card">
  <div class="icon-slot">
    <svg><!-- Feature icon --></svg>
  </div>
  <h3 class="headline">Feature Title</h3>
  <p class="description">Feature description text goes here...</p>
  <a href="#" class="cta-link">Learn more →</a>
</div>
```

**Styles:**
```css
.feature-card {
  background: var(--color-white);
  border: 1px solid var(--color-gray-light);
  border-radius: 12px;
  padding: var(--space-lg);
  text-align: center;
  transition: all 0.2s ease;
}

.feature-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(104, 44, 130, 0.1);
}

.feature-card .icon-slot {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--space-sm);
  color: var(--color-primary);
}

.feature-card .headline {
  font: var(--text-h3);
  color: var(--color-black);
  margin: 0 0 var(--space-sm);
}

.feature-card .description {
  font: var(--text-body);
  color: var(--color-gray-dark);
  margin: 0 0 var(--space-md);
}

.feature-card .cta-link {
  font: var(--text-body);
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}
```

### **4. KPI Card**
**Structure:** Large Value + Label + Trend Indicator

```html
<div class="kpi-card">
  <div class="kpi-value">1,247</div>
  <div class="kpi-label">Active Routes</div>
  <div class="kpi-trend positive">
    <span class="trend-icon">↗</span>
    <span class="trend-value">+12.5%</span>
  </div>
</div>
```

**Styles:**
```css
.kpi-card {
  background: var(--color-white);
  border: 1px solid var(--color-gray-light);
  border-radius: 12px;
  padding: var(--space-lg);
  text-align: center;
  min-width: 200px;
}

.kpi-value {
  font: var(--text-h1);
  color: var(--color-primary);
  margin: 0 0 var(--space-xs);
}

.kpi-label {
  font: var(--text-body);
  color: var(--color-gray-dark);
  margin: 0 0 var(--space-sm);
}

.kpi-trend {
  font: var(--text-body-small);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
}

.kpi-trend.positive {
  color: #22c55e; /* Green */
}

.kpi-trend.negative {
  color: #ef4444; /* Red */
}
```

### **5. Route Map Frame**
**Structure:** Map Container + Route Overlay + Location Markers

```html
<div class="route-map-frame">
  <div class="map-container">
    <!-- Map implementation (Google Maps, Mapbox, etc.) -->
    <div id="map-view"></div>
  </div>
  <div class="map-controls">
    <button class="map-control">Zoom In</button>
    <button class="map-control">Zoom Out</button>
    <button class="map-control">Reset View</button>
  </div>
</div>
```

**Styles:**
```css
.route-map-frame {
  width: 100%;
  max-width: 800px;
  height: 600px;
  border: 1px solid var(--color-gray-light);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  background: var(--color-gray-light);
}

.map-container {
  width: 100%;
  height: 100%;
}

.map-controls {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.map-control {
  background: var(--color-white);
  border: 1px solid var(--color-gray-light);
  border-radius: 6px;
  padding: var(--space-xs);
  font: var(--text-body-small);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

---

## 📄 **Page Layout Specifications**

### **1. Home Page**
```html
<!DOCTYPE html>
<html>
<head>
  <title>RouteForce Pro</title>
</head>
<body>
  <!-- Header Navigation -->
  <header class="header-nav">...</header>
  
  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-content">
      <h1>Optimize Your Routes with AI</h1>
      <p>RouteForce Pro uses advanced algorithms to create the most efficient delivery routes.</p>
      <div class="hero-ctas">
        <button class="btn btn-primary">Start Free Trial</button>
        <button class="btn btn-secondary">Watch Demo</button>
      </div>
    </div>
    <div class="hero-image">
      <!-- Route visualization graphic -->
    </div>
  </section>
  
  <!-- Features Grid -->
  <section class="features-grid">
    <div class="container">
      <h2>Powerful Features</h2>
      <div class="grid">
        <div class="feature-card">...</div>
        <div class="feature-card">...</div>
        <div class="feature-card">...</div>
      </div>
    </div>
  </section>
  
  <!-- Progress Overview -->
  <section class="progress-overview">
    <div class="step-bar">...</div>
  </section>
  
  <!-- Testimonials -->
  <section class="testimonials">
    <div class="testimonial-card">...</div>
    <div class="testimonial-card">...</div>
  </section>
  
  <!-- Footer -->
  <footer class="footer-nav">...</footer>
</body>
</html>
```

### **2. Dashboard Page**
```html
<!-- Header -->
<header class="header-nav">...</header>

<!-- KPI Row -->
<section class="kpi-dashboard">
  <div class="kpi-grid">
    <div class="kpi-card">...</div>
    <div class="kpi-card">...</div>
    <div class="kpi-card">...</div>
    <div class="kpi-card">...</div>
  </div>
</section>

<!-- Charts Row -->
<section class="charts-row">
  <div class="chart-container">
    <canvas id="line-chart"></canvas>
  </div>
  <div class="chart-container">
    <canvas id="bar-chart"></canvas>
  </div>
</section>

<!-- System Health & Activity Feed -->
<section class="system-overview">
  <div class="system-health">
    <div class="status-widget">...</div>
  </div>
  <div class="activity-feed">
    <div class="feed-item">...</div>
    <div class="feed-item">...</div>
  </div>
</section>
```

### **3. Route Generator Page**
```html
<!-- Header -->
<header class="header-nav">...</header>

<!-- Progress Steps -->
<section class="progress-steps">
  <div class="step-bar">...</div>
</section>

<!-- File Upload -->
<section class="upload-section">
  <div class="file-upload-box">...</div>
</section>

<!-- Configuration Form -->
<section class="config-form">
  <form>
    <div class="form-row">
      <select class="dropdown">...</select>
      <input type="number" class="number-input">
      <label class="checkbox">...</label>
    </div>
  </form>
</section>

<!-- Generate Button -->
<section class="generate-section">
  <button class="btn btn-primary btn-large">Generate Optimal Routes</button>
</section>

<!-- Results -->
<section class="results-section">
  <div class="summary-box">...</div>
  <div class="route-map-frame">...</div>
</section>
```

---

## 🎯 **Implementation Guidelines**

### **Grid System**
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
}

.grid {
  display: grid;
  gap: var(--space-lg);
}

.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

@media (max-width: 768px) {
  .grid-2, .grid-3, .grid-4 {
    grid-template-columns: 1fr;
  }
}
```

### **Responsive Breakpoints**
```css
/* Mobile First */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

---

## ✅ **Next Steps**

1. **Use any design tool** (Canva, Sketch, Adobe XD, or even HTML/CSS)
2. **Implement with your preferred framework** (React, Vue, vanilla CSS)
3. **Copy-paste these exact specifications** - no guesswork needed
4. **All measurements, colors, and styles are defined** - pixel-perfect implementation ready

**This complete specification provides everything needed for implementation!** 🚀
