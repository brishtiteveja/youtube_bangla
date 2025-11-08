# Proxy Setup Guide - Webshare Integration

This guide explains how to set up **Webshare static residential proxies** to avoid YouTube IP blocking when fetching transcripts.

## Why Use Proxies?

YouTube may block or rate-limit transcript requests if:
- You make too many requests from the same IP
- You're using a datacenter/cloud IP (AWS, Google Cloud, etc.)
- Multiple users share the same IP address

**Webshare static residential proxies** solve this by routing requests through residential IPs that YouTube trusts.

## Quick Setup (5 minutes)

### Step 1: Get Webshare Proxies

1. **Sign up** at https://www.webshare.io/
2. **Choose a plan**:
   - **Free Trial**: 10 proxies (perfect for testing)
   - **Starter Plan**: Static residential proxies recommended
3. **Go to Dashboard** → Proxy → Proxy List
4. **Note your credentials**:
   - Proxy Host: `proxy.webshare.io`
   - Proxy Port: `80` or `443`
   - Username: `xxxxxxx-xxxxx`
   - Password: `xxxxxxxxxx`

### Step 2: Configure Your App

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file**:
   ```bash
   nano .env
   # or use any text editor
   ```

3. **Add your Webshare credentials**:
   ```env
   # Enable proxy
   USE_PROXY=true

   # Webshare credentials
   PROXY_HOST=proxy.webshare.io
   PROXY_PORT=80
   PROXY_USERNAME=your-username-here
   PROXY_PASSWORD=your-password-here
   ```

4. **Save and close** the file

### Step 3: Install Dependencies

```bash
# Install updated dependencies (includes python-dotenv)
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

### Step 4: Run the App

```bash
streamlit run app.py
```

That's it! Your app now routes transcript requests through Webshare proxies.

## Verification

To verify proxies are working:

1. **Check console output** when fetching transcripts (you may see proxy-related logs)
2. **Test with a video** that was previously blocked
3. **Monitor your Webshare dashboard** to see proxy usage

## Configuration Details

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `USE_PROXY` | Yes | Enable/disable proxies | `true` or `false` |
| `PROXY_HOST` | Yes | Proxy server hostname | `proxy.webshare.io` |
| `PROXY_PORT` | Yes | Proxy server port | `80` or `443` |
| `PROXY_USERNAME` | Yes | Your Webshare username | `abc123-def456` |
| `PROXY_PASSWORD` | Yes | Your Webshare password | `secretpassword` |

### Proxy Configuration in Code

The proxy configuration is handled automatically in [src/config.py](src/config.py):

```python
@classmethod
def get_proxy_dict(cls):
    """Get proxy configuration as dict for youtube-transcript-api"""
    if not cls.USE_PROXY or not cls.PROXY_HOST:
        return None

    proxy_url = f"http://{cls.PROXY_USERNAME}:{cls.PROXY_PASSWORD}@{cls.PROXY_HOST}:{cls.PROXY_PORT}"
    return {
        'http': proxy_url,
        'https': proxy_url
    }
```

The `TranscriptFetcher` class in [src/transcript_api.py](src/transcript_api.py) uses this configuration:

```python
def __init__(self, use_proxy: bool = None):
    self.use_proxy = use_proxy if use_proxy is not None else Config.USE_PROXY
    proxies = Config.get_proxy_dict() if self.use_proxy else None

    if proxies:
        self.api = YouTubeTranscriptApi(proxies=proxies)
    else:
        self.api = YouTubeTranscriptApi()
```

## Troubleshooting

### Issue: "Connection refused" or "Proxy error"

**Cause**: Incorrect proxy credentials or host/port

**Solution**:
1. Double-check your Webshare credentials
2. Verify proxy host is `proxy.webshare.io`
3. Try both ports: `80` (HTTP) and `443` (HTTPS)
4. Check your Webshare subscription is active

### Issue: Still getting IP blocked

**Cause**: Proxy not enabled or rotating through blocked IPs

**Solution**:
1. Verify `USE_PROXY=true` in your `.env` file
2. Try a different proxy from your Webshare list
3. Use **static residential proxies** (not datacenter proxies)
4. Wait a few minutes between requests

### Issue: "ModuleNotFoundError: No module named 'dotenv'"

**Cause**: python-dotenv not installed

**Solution**:
```bash
pip install python-dotenv
# or
pip install -r requirements.txt
```

### Issue: Proxies slow down transcript fetching

**Cause**: Network latency through proxy

**Solution**:
- This is normal - proxies add 100-500ms latency
- Choose proxies closer to your region
- Use Webshare's "high priority network" (available in paid plans)
- For large batch jobs, the stability is worth the slight slowdown

## Webshare Plan Recommendations

### For Personal Use / Testing
- **Free Trial**: 10 proxies, perfect for testing
- Enough for fetching transcripts from a few channels

### For Medium Use (100-1000 videos/day)
- **Starter Plan**: $2.99/month
- 10 static residential proxies
- 250GB bandwidth
- Best value for money

### For Heavy Use (1000+ videos/day)
- **Professional Plan**: $49.99/month
- 100 static residential proxies
- 1TB bandwidth
- High priority network

### Your Current Plan
Based on your screenshot:
- ✅ **Active subscription**
- ✅ **High Priority Network** enabled
- ✅ **1 IP Authorization** available
- ✅ **3/3 Sub-users** available
- ✅ **10/10 Proxy Replacements** available

This is perfect for YouTube transcript collection!

## Security Best Practices

1. **Never commit `.env` to git**
   - Already in `.gitignore`
   - Contains sensitive credentials

2. **Use environment variables**
   - Don't hardcode credentials in code
   - Use `.env` file for local development

3. **Rotate credentials regularly**
   - Change passwords every 90 days
   - Use Webshare's "Reset Password" feature

4. **Monitor usage**
   - Check Webshare dashboard for unusual activity
   - Set up usage alerts if available

## Alternative Proxy Providers

If you prefer other providers, the configuration works with:

- **Bright Data** (formerly Luminati)
- **Smartproxy**
- **Oxylabs**
- **IPRoyal**
- Any HTTP/HTTPS proxy service

Just update the `.env` file with your provider's credentials.

## Disabling Proxies

To temporarily disable proxies without removing credentials:

```env
USE_PROXY=false
```

Or remove the `.env` file entirely - the app will work without proxies (with potential IP blocking risks).

## Advanced: Proxy Rotation

For advanced users who want to rotate through multiple proxies:

1. Get multiple proxy credentials from Webshare
2. Modify [src/transcript_api.py](src/transcript_api.py) to implement rotation logic
3. Store proxy list in config or external file
4. Rotate on each request or after X requests

Example rotation logic:
```python
import random

class TranscriptFetcher:
    def __init__(self):
        self.proxy_list = [
            {'http': 'http://user1:pass1@proxy1:80', 'https': '...'},
            {'http': 'http://user2:pass2@proxy2:80', 'https': '...'},
        ]

    def get_random_proxy(self):
        return random.choice(self.proxy_list)
```

## Summary

✅ **Proxies prevent IP blocking**
✅ **Webshare offers reliable static residential IPs**
✅ **Setup takes only 5 minutes**
✅ **Configuration is secure (via .env file)**
✅ **Can be enabled/disabled easily**

For questions or issues, check:
- [Webshare Documentation](https://docs.webshare.io/)
- [YouTube Transcript API Docs](https://github.com/jdepoix/youtube-transcript-api)
- Project [FIX_SUMMARY.md](FIX_SUMMARY.md)

---

**Status**: ✅ Proxy support fully integrated!
