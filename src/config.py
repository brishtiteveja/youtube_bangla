"""
Configuration Module
Centralized configuration for the application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (override=True to refresh)
load_dotenv(override=True)


class Config:
    """Application configuration"""

    # API Configuration
    YOUTUBE_API_KEY = 'AIzaSyBHJCUTQ4WEJQrpmqAIDuQfgweMRJxd1cc'

    # Default Settings
    DEFAULT_CHANNEL = "Pinaki Bhattacharya"
    DEFAULT_VIDEO_COUNT = 50
    MAX_VIDEO_COUNT = 200
    MIN_VIDEO_COUNT = 10

    # Language Settings
    DEFAULT_LANGUAGES = ['bn', 'en', 'hi']
    LANGUAGE_OPTIONS = {
        'Bangla (বাংলা)': 'bn',
        'English': 'en',
        'Hindi (हिन्दी)': 'hi',
        'Auto-detect': 'auto'
    }

    # File Paths
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
    DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')

    # Database
    CHANNEL_DATABASE_PATH = os.path.join(DATA_DIR, 'bangladeshi_channels.json')

    # UI Settings
    PAGE_TITLE = "YouTube Transcript Collector - Bangladesh"
    PAGE_ICON = "🇧🇩"
    LAYOUT = "wide"

    # Rate Limiting
    API_RATE_LIMIT_DELAY = 0.3  # seconds between API calls

    # Proxy Configuration (for transcript fetching)
    USE_PROXY = os.getenv('USE_PROXY', 'false').lower() == 'true'

    # Webshare API Key for dynamic proxy rotation
    WEBSHARE_API_KEY = os.getenv('WEBSHARE_API_KEY', '')

    # Proxy rotation mode: 'api', 'manual', or 'rotating' (Webshare rotating residential)
    PROXY_MODE = os.getenv('PROXY_MODE', 'api')  # 'api', 'manual', or 'rotating'

    # Rotating residential proxy settings (used if PROXY_MODE='rotating')
    ROTATING_PROXY_HOST = os.getenv('ROTATING_PROXY_HOST', '')
    ROTATING_PROXY_PORT = os.getenv('ROTATING_PROXY_PORT', '')
    ROTATING_PROXY_USERNAME = os.getenv('ROTATING_PROXY_USERNAME', '')
    ROTATING_PROXY_PASSWORD = os.getenv('ROTATING_PROXY_PASSWORD', '')

    # Manual proxy settings (used only if PROXY_MODE='manual')
    PROXY_HOST = os.getenv('PROXY_HOST', '')
    PROXY_PORT = os.getenv('PROXY_PORT', '')
    PROXY_USERNAME = os.getenv('PROXY_USERNAME', '')
    PROXY_PASSWORD = os.getenv('PROXY_PASSWORD', '')

    # Retry settings for transcript fetching
    MAX_RETRY_ATTEMPTS = 5  # Number of retry attempts before giving up

    # Proxy manager instance (lazy loaded)
    _proxy_manager = None

    @classmethod
    def get_proxy_manager(cls):
        """Get or create proxy manager instance"""
        if not cls.USE_PROXY or not cls.WEBSHARE_API_KEY:
            return None

        if cls._proxy_manager is None and cls.PROXY_MODE == 'api':
            from proxy_manager import WebshareProxyManager
            cls._proxy_manager = WebshareProxyManager(cls.WEBSHARE_API_KEY)

        return cls._proxy_manager

    # Rotating residential proxy counter
    _residential_proxy_counter = 0
    _residential_proxy_count = 10  # Number of residential proxies available

    @classmethod
    def get_proxy_dict(cls):
        """Get proxy configuration as dict for requests/youtube-transcript-api"""
        if not cls.USE_PROXY:
            return None

        # Mode 1: Rotating residential proxy - manually rotate through numbered proxies
        if cls.PROXY_MODE == 'rotating' and cls.ROTATING_PROXY_HOST:
            # For numbered residential proxies (residential-1, residential-2, etc.)
            # Extract base username (without number suffix)
            base_username = cls.ROTATING_PROXY_USERNAME

            # If username already has a number, remove it to get base
            if '-' in base_username:
                parts = base_username.rsplit('-', 1)
                if parts[-1].isdigit():
                    base_username = '-'.join(parts[:-1])

            # Round-robin through residential proxies
            cls._residential_proxy_counter = (cls._residential_proxy_counter % cls._residential_proxy_count) + 1
            numbered_username = f"{base_username}-{cls._residential_proxy_counter}"

            proxy_url = f"http://{numbered_username}:{cls.ROTATING_PROXY_PASSWORD}@{cls.ROTATING_PROXY_HOST}:{cls.ROTATING_PROXY_PORT}"
            return {
                'http': proxy_url,
                'https': proxy_url,
                'rotating': True,
                'proxy_number': cls._residential_proxy_counter
            }

        # Mode 2: Use Webshare API for rotation (datacenter proxies)
        if cls.PROXY_MODE == 'api' and cls.WEBSHARE_API_KEY:
            manager = cls.get_proxy_manager()
            if manager:
                return manager.get_next_proxy()
            return None

        # Mode 3: Use manual single proxy
        if cls.PROXY_HOST and cls.PROXY_PORT:
            proxy_url = f"http://{cls.PROXY_USERNAME}:{cls.PROXY_PASSWORD}@{cls.PROXY_HOST}:{cls.PROXY_PORT}"
            return {
                'http': proxy_url,
                'https': proxy_url
            }

        return None

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.DOCS_DIR, exist_ok=True)
