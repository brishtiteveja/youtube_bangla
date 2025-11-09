"""
Test Script for Proxy Rotation and Retry Mechanism
Tests the rotating residential proxy configuration and retry logic
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from transcript_api import TranscriptProcessor

def test_proxy_config():
    """Test proxy configuration"""
    print("=" * 70)
    print("🔧 TESTING PROXY CONFIGURATION")
    print("=" * 70)

    print(f"USE_PROXY: {Config.USE_PROXY}")
    print(f"PROXY_MODE: {Config.PROXY_MODE}")
    print(f"MAX_RETRY_ATTEMPTS: {Config.MAX_RETRY_ATTEMPTS}")

    if Config.PROXY_MODE == 'rotating':
        print(f"\n📡 Rotating Proxy Settings:")
        print(f"  Host: {Config.ROTATING_PROXY_HOST}")
        print(f"  Port: {Config.ROTATING_PROXY_PORT}")
        print(f"  Username: {Config.ROTATING_PROXY_USERNAME[:10]}***")

        proxy_dict = Config.get_proxy_dict()
        if proxy_dict:
            print(f"\n✅ Proxy configured successfully!")
            print(f"  Proxy URL format: http://username:password@{Config.ROTATING_PROXY_HOST}:{Config.ROTATING_PROXY_PORT}")
        else:
            print("\n❌ Proxy configuration failed!")

    print("\n")

def test_transcript_fetch():
    """Test transcript fetching with retry mechanism"""
    print("=" * 70)
    print("📝 TESTING TRANSCRIPT FETCH WITH RETRY")
    print("=" * 70)

    # Test video - Pinaki Bhattacharya video (usually has Bangla transcript)
    test_video_id = "m4ri2oiiKik"
    test_title = "Test Video"

    print(f"Video ID: {test_video_id}")
    print(f"Languages: ['bn', 'en', 'hi']")
    print(f"Max retries: {Config.MAX_RETRY_ATTEMPTS}")
    print(f"Using proxy: {Config.USE_PROXY}")
    print(f"\nFetching transcript...\n")

    # Create processor
    processor = TranscriptProcessor()

    # Fetch transcript
    result = processor.get_and_format(
        video_id=test_video_id,
        video_title=test_title,
        languages=['bn', 'en', 'hi'],
        format_type='timestamped'
    )

    # Display results
    if result['success']:
        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)

        metadata = result['metadata']
        print(f"Language: {metadata['language_code']}")
        print(f"Type: {'Auto-generated' if metadata['is_generated'] else 'Manual'}")
        print(f"Entries: {metadata['entry_count']}")

        # Show first 5 lines of transcript
        lines = result['formatted_text'].split('\n')[:5]
        print(f"\n📄 First 5 lines:")
        for line in lines:
            print(f"  {line}")
        print("  ...")

    else:
        print("\n" + "=" * 70)
        print("❌ FAILED!")
        print("=" * 70)
        print(f"Error: {result['error']}")
        if 'attempts' in result:
            print(f"Attempts made: {result['attempts']}")

    print("\n")

def main():
    """Run all tests"""
    print("\n")
    print("🧪 YouTube Transcript Collector - Proxy & Retry Test")
    print("=" * 70)
    print("\n")

    # Test 1: Proxy configuration
    test_proxy_config()

    # Test 2: Transcript fetch with retry
    test_transcript_fetch()

    print("=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print("\n")

if __name__ == "__main__":
    main()