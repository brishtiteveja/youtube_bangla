# Quick Start: Webshare Proxy Setup

## 🚀 5-Minute Setup

### 1. Get Webshare Account
- Sign up: https://www.webshare.io/
- Get 10 free proxies (trial)

### 2. Get Your Credentials
Go to **Dashboard → Proxy → Proxy List**, note:
- Host: `proxy.webshare.io`
- Port: `80`
- Username: (your username)
- Password: (your password)

### 3. Configure App
```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env
```

Add your credentials:
```env
USE_PROXY=true
PROXY_HOST=proxy.webshare.io
PROXY_PORT=80
PROXY_USERNAME=your-username
PROXY_PASSWORD=your-password
```

### 4. Run
```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## ✅ Verification

Test that proxies work:
1. Click "Get Transcript" on any video
2. Should work without IP blocking errors
3. Check Webshare dashboard for proxy usage

## 🔄 Your Current Setup

Based on your Webshare plan:
- ✅ Active subscription
- ✅ High Priority Network
- ✅ 10 proxy replacements available
- ✅ Thread limit: 500 (more than enough)

## 💡 Tips

**Enable only when needed:**
```env
USE_PROXY=false  # Disable (faster, but may get blocked)
USE_PROXY=true   # Enable (slower, but stable)
```

**For batch processing:**
- Keep proxies enabled
- Prevents IP bans
- Worth the slight slowdown

## 📚 More Info

- Full guide: [PROXY_SETUP.md](PROXY_SETUP.md)
- Troubleshooting: [README.md](README.md#troubleshooting)
- Fix details: [FIX_SUMMARY.md](FIX_SUMMARY.md)

---

**That's it!** Your transcript fetching will now work reliably. 🎉
