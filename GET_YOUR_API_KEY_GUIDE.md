# 🔑 How to Get Your Anthropic API Key (Step-by-Step)

## Important: I Cannot Get an API Key For You ⚠️

API keys are **personal credentials** that must be created by **you** through your own Anthropic account. This ensures security and proper billing.

## 🚀 Step-by-Step Guide to Get Your API Key

### Step 1: Create Anthropic Account
1. Go to: **https://console.anthropic.com/**
2. Click "Sign Up" if you don't have an account
3. Verify your email address
4. Complete account setup

### Step 2: Add Billing Information
1. Go to "Billing" in the console
2. Add a payment method (credit card)
3. **You get $5 FREE credit** to start!
4. No charges until you use the $5 credit

### Step 3: Create API Key
1. Navigate to "API Keys" section
2. Click "Create Key" or "New API Key"
3. Give it a name (e.g., "RouteForce Development")
4. **Copy the key immediately** - you won't see it again!
5. Store it securely

### Step 4: Configure Your Project
Once you have your API key, add it to your `.env` file:

```bash
# Edit your .env file
vim .env

# Replace this line:
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# With your actual key:
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

### Step 5: Test Your Setup
```bash
# Run the setup script I created
./setup_claude_opus_4.sh

# Or test manually
python3 app.py
```

## 🔒 Security Best Practices

- ✅ **Never share** your API key publicly
- ✅ **Store in .env file** (already in .gitignore)
- ✅ **Rotate keys** periodically
- ✅ **Monitor usage** in console
- ❌ **Don't commit keys** to git
- ❌ **Don't paste in chat/email**

## 💰 Pricing Information

- **Free credit**: $5 to start
- **Claude Opus 4**: ~$15 per 1M input tokens, ~$75 per 1M output tokens
- **Example costs**:
  - Simple chat: ~$0.01-0.05 per message
  - Route optimization: ~$0.10-0.50 per analysis
  - Much cheaper than $200/month subscription!

## 🎯 Quick Links

- **Console**: https://console.anthropic.com/
- **API Keys**: https://console.anthropic.com/settings/keys
- **Billing**: https://console.anthropic.com/settings/billing
- **Documentation**: https://docs.anthropic.com/

## ✅ Once You Have Your Key

Your MCP configuration is already set up! Just:
1. Add your key to `.env`
2. Restart VS Code
3. Claude Opus 4 will appear in your model dropdown!

**OR** use the Flask API integration that's ready to go:
```bash
python3 app.py
curl -X POST http://localhost:5000/claude/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Claude Opus 4!"}'
```

## 🚨 Need Help?

If you run into issues:
1. Check console.anthropic.com for account status
2. Verify billing information is added
3. Make sure API key is copied correctly
4. Run `./setup_claude_opus_4.sh` for automated testing

**Remember**: The API key setup only takes 2-3 minutes, and you'll have Claude Opus 4 access immediately! 🚀
