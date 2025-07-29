# EXACT DNS FIX - Add This Record to Squarespace

## 🎯 What You Need to Add

In your Squarespace DNS Settings (where you just took the screenshot), click **"ADD PRESET"** and add:

```
Type: CNAME
Host: app
Data: routeforcepro.netlify.app
TTL: 4 hrs (or default)
Priority: 0 (or leave blank)
```

## 📋 Step-by-Step Instructions

1. **In your Squarespace DNS Settings** (where you are now)
2. **Click "ADD PRESET"** (button visible in your screenshot)
3. **Select "CNAME"** from the dropdown
4. **Fill in these exact values:**
   - **Host/Name**: `app`
   - **Points to/Data**: `routeforcepro.netlify.app`
   - **TTL**: `4 hrs` (matches your other records)

## 🔍 What This Does

This creates the subdomain `app.routeforcepro.com` and points it to your Netlify site.

## ✅ Expected Result

After adding this record, your DNS table should show:

| HOST | TYPE | PRIORITY | TTL | DATA |
|------|------|----------|-----|------|
| @ | A | 0 | 4 hrs | 198.49.23.144 |
| @ | A | 0 | 4 hrs | 198.49.23.145 |
| @ | A | 0 | 4 hrs | 198.185.159.145 |
| @ | A | 0 | 4 hrs | 198.185.159.144 |
| www | CNAME | 0 | 4 hrs | ext-sq.squarespace.com |
| **app** | **CNAME** | **0** | **4 hrs** | **routeforcepro.netlify.app** |
| @ | HTTPS | 0 | 4 hrs | [existing HTTPS record] |

## ⏰ Timeline After Adding

1. **Immediately**: Record is saved in Squarespace
2. **15-60 minutes**: DNS starts propagating globally
3. **1-24 hours**: Full global propagation complete
4. **SSL**: Netlify will auto-issue SSL certificate once DNS works

## 🧪 Test Commands (After Adding)

```bash
# Test DNS propagation (wait 15+ minutes after adding)
nslookup app.routeforcepro.com

# Should eventually return:
# app.routeforcepro.com canonical name = routeforcepro.netlify.app
```

## 🚨 Important Notes

- **Don't modify existing records** - they're correct for your main site
- **Only add the new CNAME record** for `app` subdomain
- **Use exact value**: `routeforcepro.netlify.app` (no https://, no trailing dot)
- **Wait for propagation** - DNS changes take time

---

**Next Step: Click "ADD PRESET" and add the CNAME record above!**
