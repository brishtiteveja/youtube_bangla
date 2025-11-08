"""
Proxy Manager Module
Handles Webshare proxy rotation and management
"""

import requests
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os


class WebshareProxyManager:
    """Manages Webshare proxy rotation"""

    def __init__(self, api_key: str, cache_duration_minutes: int = 60):
        """
        Initialize Webshare Proxy Manager

        Args:
            api_key: Your Webshare API key
            cache_duration_minutes: How long to cache proxy list (default: 60 minutes)
        """
        self.api_key = api_key
        self.base_url = "https://proxy.webshare.io/api/v2"
        self.proxies = []
        self.cache_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            '.proxy_cache.json'
        )
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        self.last_fetch = None
        self.current_index = 0

    def fetch_proxy_list(self, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch proxy list from Webshare API

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            List of proxy dictionaries
        """
        # Check if we have valid cache
        if not force_refresh and self._is_cache_valid():
            print("📦 Using cached proxy list")
            return self.proxies

        print("🔄 Fetching proxy list from Webshare API...")

        try:
            response = requests.get(
                f"{self.base_url}/proxy/list/?mode=direct",
                headers={"Authorization": f"Token {self.api_key}"},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                proxy_list = data.get('results', [])

                # Transform to our format
                self.proxies = [
                    {
                        'host': proxy['proxy_address'],
                        'port': proxy['port'],
                        'username': proxy['username'],
                        'password': proxy['password'],
                        'country_code': proxy.get('country_code', 'Unknown'),
                        'city': proxy.get('city_name', 'Unknown'),
                        'valid': proxy.get('valid', True)
                    }
                    for proxy in proxy_list
                ]

                # Filter only valid proxies
                self.proxies = [p for p in self.proxies if p['valid']]

                self.last_fetch = datetime.now()
                self._save_cache()

                print(f"✅ Fetched {len(self.proxies)} working proxies")
                return self.proxies

            elif response.status_code == 401:
                print(f"❌ Authentication failed. Check your API key.")
                return []
            else:
                print(f"⚠️  API returned status {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch proxy list: {str(e)}")
            # Try to load from cache if available
            if self._load_cache():
                print("📦 Loaded stale proxy list from cache")
                return self.proxies
            return []

    def get_next_proxy(self) -> Optional[Dict]:
        """
        Get next proxy in rotation

        Returns:
            Proxy dict in format for requests library
        """
        if not self.proxies:
            self.fetch_proxy_list()

        if not self.proxies:
            return None

        # Round-robin rotation
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)

        # Format for requests library
        proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"

        return {
            'http': proxy_url,
            'https': proxy_url,
            'info': {
                'host': proxy['host'],
                'country': proxy['country_code'],
                'city': proxy['city']
            }
        }

    def get_random_proxy(self) -> Optional[Dict]:
        """
        Get random proxy from list

        Returns:
            Proxy dict in format for requests library
        """
        if not self.proxies:
            self.fetch_proxy_list()

        if not self.proxies:
            return None

        proxy = random.choice(self.proxies)

        # Format for requests library
        proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"

        return {
            'http': proxy_url,
            'https': proxy_url,
            'info': {
                'host': proxy['host'],
                'country': proxy['country_code'],
                'city': proxy['city']
            }
        }

    def get_all_proxies(self) -> List[Dict]:
        """
        Get all available proxies

        Returns:
            List of proxy dicts
        """
        if not self.proxies:
            self.fetch_proxy_list()

        return self.proxies

    def get_proxy_count(self) -> int:
        """Get number of available proxies"""
        if not self.proxies:
            self.fetch_proxy_list()
        return len(self.proxies)

    def _is_cache_valid(self) -> bool:
        """Check if proxy cache is still valid"""
        if not self.last_fetch:
            return self._load_cache()

        age = datetime.now() - self.last_fetch
        return age < self.cache_duration

    def _save_cache(self):
        """Save proxy list to cache file"""
        try:
            cache_data = {
                'proxies': self.proxies,
                'last_fetch': self.last_fetch.isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"⚠️  Could not save proxy cache: {str(e)}")

    def _load_cache(self) -> bool:
        """Load proxy list from cache file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.proxies = cache_data.get('proxies', [])
                    self.last_fetch = datetime.fromisoformat(cache_data.get('last_fetch'))
                    return len(self.proxies) > 0
        except Exception as e:
            print(f"⚠️  Could not load proxy cache: {str(e)}")
        return False

    def print_stats(self):
        """Print proxy statistics"""
        if not self.proxies:
            self.fetch_proxy_list()

        print("\n📊 Proxy Statistics")
        print("=" * 70)
        print(f"Total Proxies: {len(self.proxies)}")

        if self.proxies:
            countries = {}
            for proxy in self.proxies:
                country = proxy['country_code']
                countries[country] = countries.get(country, 0) + 1

            print("\nProxies by Country:")
            for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True):
                print(f"  {country}: {count}")

            print(f"\nCache Status: {'✅ Valid' if self._is_cache_valid() else '⚠️  Expired'}")
            if self.last_fetch:
                print(f"Last Fetched: {self.last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")
