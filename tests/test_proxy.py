#!/usr/bin/env python3
"""
Test Webshare Auto-Rotating Proxy
Quick test to verify proxy configuration works
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
import requests

def test_proxy():
    """Test the proxy configuration"""

    print("=" * 60)
    print("Webshare Auto-Rotating Proxy Test")
    print("=" * 60)
    print()

    # Get proxy config
    print("Getting proxy configuration...")
    proxy_dict = Config.get_proxy_dict()

    if not proxy_dict:
        print("❌ No proxy configured")
        return False

    print(f"✅ Proxy configured")
    print(f"   Mode: {Config.PROXY_MODE}")
    print(f"   Host: {Config.ROTATING_PROXY_HOST}")
    print(f"   Username: {Config.ROTATING_PROXY_USERNAME}")
    print()

    # Test connection
    print("Testing proxy connection...")
    print("Making 3 requests to check IP rotation...")
    print()

    for i in range(3):
        try:
            proxies = {k: v for k, v in proxy_dict.items() if k in ['http', 'https']}

            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies,
                timeout=10
            )

            if response.status_code == 200:
                ip_data = response.json()
                print(f"✅ Request {i+1}: Success - IP: {ip_data.get('ip')}")
            else:
                print(f"❌ Request {i+1}: Failed with status {response.status_code}")

        except Exception as e:
            print(f"❌ Request {i+1}: Error - {str(e)}")

    print()
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)
    print()
    print("Note: If IPs are different, Webshare rotation is working!")
    print("If they're the same, that's OK - rotation happens per endpoint")

    return True


if __name__ == '__main__':
    try:
        test_proxy()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)