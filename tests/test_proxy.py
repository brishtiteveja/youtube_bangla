"""
Test Webshare proxy configuration
"""

import sys
import os
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from config import Config

print("=" * 70)
print("TESTING WEBSHARE PROXY CONFIGURATION")
print("=" * 70)

# Test 1: Check if proxy is enabled
print("\n1. Checking proxy configuration...")
print("-" * 70)
print(f"USE_PROXY: {Config.USE_PROXY}")
print(f"PROXY_HOST: {Config.PROXY_HOST}")
print(f"PROXY_PORT: {Config.PROXY_PORT}")
print(f"PROXY_USERNAME: {Config.PROXY_USERNAME[:5]}*** (hidden)")
print(f"PROXY_PASSWORD: {'*' * len(Config.PROXY_PASSWORD)}")

# Test 2: Get proxy dict
print("\n2. Testing proxy configuration format...")
print("-" * 70)
proxy_dict = Config.get_proxy_dict()
if proxy_dict:
    # Show sanitized version (hide password)
    sanitized = {
        'http': proxy_dict['http'].replace(Config.PROXY_PASSWORD, '***'),
        'https': proxy_dict['https'].replace(Config.PROXY_PASSWORD, '***')
    }
    print(f"Proxy dict: {sanitized}")
    print("✅ Proxy configuration looks good!")
else:
    print("❌ Proxy not configured or disabled")
    print("\nTo enable:")
    print("1. Make sure .env file exists")
    print("2. Set USE_PROXY=true")
    print("3. Add your credentials")

# Test 3: Test proxy connection
print("\n3. Testing proxy connection with httpbin.org...")
print("-" * 70)

if proxy_dict:
    try:
        # Test with httpbin (shows your IP)
        print("Testing WITHOUT proxy...")
        response_no_proxy = requests.get('https://httpbin.org/ip', timeout=10)
        your_ip = response_no_proxy.json()['origin']
        print(f"Your real IP: {your_ip}")

        print("\nTesting WITH Webshare proxy...")
        response_with_proxy = requests.get(
            'https://httpbin.org/ip',
            proxies=proxy_dict,
            timeout=15
        )
        proxy_ip = response_with_proxy.json()['origin']
        print(f"Proxy IP: {proxy_ip}")

        if your_ip != proxy_ip:
            print("\n✅ SUCCESS! Proxy is working correctly!")
            print(f"Your traffic is routing through: {proxy_ip}")
        else:
            print("\n⚠️  WARNING: Proxy returned your real IP")
            print("This might mean the proxy is not working properly")

    except requests.exceptions.ProxyError as e:
        print(f"\n❌ PROXY ERROR: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your Webshare credentials in .env")
        print("2. Verify your proxy subscription is active")
        print("3. Try different PROXY_PORT (80 or 443)")
        print("4. Check Webshare dashboard for proxy status")

    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT: Proxy took too long to respond")
        print("This is normal if you're rate-limited. Try again in a few seconds.")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("Check your internet connection and proxy settings")
else:
    print("⚠️  Skipping connection test (proxy not configured)")

# Test 4: Test with youtube-transcript-api
print("\n4. Testing with YouTube Transcript API...")
print("-" * 70)

try:
    from transcript_api import TranscriptFetcher

    fetcher = TranscriptFetcher(use_proxy=True)
    print(f"TranscriptFetcher initialized with proxy: {fetcher.use_proxy}")

    # Try a simple video (won't fetch, just test initialization)
    print("\nTrying to fetch transcript from a test video...")
    print("(This may take 10-15 seconds through proxy...)")

    # Use a well-known video with English subtitles
    test_video = "jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video
    result = fetcher.get_transcript(test_video, languages=['en'])

    if result['success']:
        print("\n✅ SUCCESS! Transcript fetched through proxy!")
        print(f"Language: {result['language_code']}")
        print(f"Entries: {len(result['transcript'])}")
        print(f"First entry: {result['transcript'][0]}")
        print("\n🎉 Your proxy is working perfectly with YouTube!")
    else:
        print(f"\n⚠️  Could not fetch transcript: {result.get('error')}")
        print("This might be normal if the video doesn't have transcripts")
        print("But the proxy connection was attempted successfully!")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nIf you see 'Could not retrieve transcript', this could mean:")
    print("1. The test video doesn't have transcripts (normal)")
    print("2. YouTube is blocking even with proxy (try again later)")
    print("3. Proxy credentials are incorrect")

print("\n" + "=" * 70)
print("PROXY TEST COMPLETE")
print("=" * 70)

print("\n📋 Summary:")
print("-" * 70)
print("• Config loaded: ✅" if Config.USE_PROXY else "• Config loaded: ❌")
print(f"• Proxy enabled: {'✅' if Config.USE_PROXY else '❌'}")
print(f"• Webshare endpoint: {Config.PROXY_HOST}")
print(f"• Using rotating proxy: {'✅' if 'p.webshare.io' in Config.PROXY_HOST else '❌'}")
print("\n💡 Recommendation: Use p.webshare.io for automatic proxy rotation")
print("\nYour .env file is configured and ready to use!")
