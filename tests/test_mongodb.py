#!/usr/bin/env python3
"""
MongoDB Cache Tests
Comprehensive tests for MongoDB caching functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from mongodb_cache import MongoDBCache
from mongodb_manager import MongoDBManager
from datetime import datetime
from typing import Dict, List


class MongoDBTester:
    """Test MongoDB cache operations"""

    def __init__(self):
        self.cache = None
        self.manager = None
        self.test_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    def setup(self) -> bool:
        """Setup test environment"""
        print("=" * 70)
        print("MongoDB Cache Tests")
        print("=" * 70)
        print()

        # Initialize manager
        print("Setting up test environment...")
        self.manager = MongoDBManager()

        if not self.manager.connected:
            print("❌ Cannot connect to MongoDB")
            return False

        # Verify setup
        is_valid, issues = self.manager.verify_setup()

        if not is_valid:
            print("⚠️  MongoDB setup has issues:")
            for issue in issues:
                print(f"   - {issue}")
            print()
            print("Attempting to fix...")

            # Try to recreate collections
            if not self.manager.recreate_collections(confirm=True):
                print("❌ Failed to fix MongoDB setup")
                return False

        # Initialize cache
        self.cache = MongoDBCache()

        if not self.cache.enabled:
            print("❌ MongoDB cache is not enabled")
            return False

        print("✅ Test environment ready")
        print()
        return True

    def test_channel_cache(self) -> bool:
        """Test channel caching"""
        print("📦 Testing CHANNEL cache...")

        test_channel = {
            'channel_id': 'TEST_CHANNEL_123',
            'title': 'Test Channel',
            'description': 'This is a test channel',
            'thumbnail': 'https://example.com/thumb.jpg',
            'subscriber_count': '1000',
            'video_count': '50',
            'uploads_playlist': 'UU_TEST_123'
        }

        # Test write
        print("   Writing channel...")
        write_success = self.cache.save_channel(test_channel)

        if not write_success:
            self.test_results['failed'].append('Channel write failed')
            print("   ❌ Write failed")
            return False

        print("   ✅ Write successful")

        # Test read
        print("   Reading channel...")
        cached_channel = self.cache.get_channel(channel_id='TEST_CHANNEL_123')

        if not cached_channel:
            self.test_results['failed'].append('Channel read failed')
            print("   ❌ Read failed")
            return False

        if cached_channel['title'] != test_channel['title']:
            self.test_results['failed'].append('Channel data mismatch')
            print("   ❌ Data mismatch")
            return False

        print(f"   ✅ Read successful: {cached_channel['title']}")

        self.test_results['passed'].append('Channel cache')
        return True

    def test_videos_cache(self) -> bool:
        """Test videos caching"""
        print("📹 Testing VIDEOS cache...")

        test_videos = [
            {
                'video_id': 'TEST_VIDEO_1',
                'title': 'Test Video 1',
                'description': 'Description for test video 1',
                'published_at': '2024-01-01T00:00:00Z',
                'thumbnail': 'https://example.com/vid1.jpg'
            },
            {
                'video_id': 'TEST_VIDEO_2',
                'title': 'Test Video 2',
                'description': 'Description for test video 2',
                'published_at': '2024-01-02T00:00:00Z',
                'thumbnail': 'https://example.com/vid2.jpg'
            }
        ]

        # Test write
        print(f"   Writing {len(test_videos)} videos...")
        write_success = self.cache.save_videos('TEST_CHANNEL_123', test_videos)

        if not write_success:
            self.test_results['failed'].append('Videos write failed')
            print("   ❌ Write failed")
            return False

        print("   ✅ Write successful")

        # Test read
        print("   Reading videos...")
        cached_videos = self.cache.get_videos('TEST_CHANNEL_123', max_results=10)

        if not cached_videos:
            self.test_results['failed'].append('Videos read failed')
            print("   ❌ Read failed")
            return False

        if len(cached_videos) < len(test_videos):
            self.test_results['warnings'].append(
                f'Expected {len(test_videos)} videos, got {len(cached_videos)}'
            )

        print(f"   ✅ Read successful: Found {len(cached_videos)} videos")

        self.test_results['passed'].append('Videos cache')
        return True

    def test_transcript_cache(self) -> bool:
        """Test transcript caching"""
        print("📝 Testing TRANSCRIPT cache...")

        test_transcript = {
            'success': True,
            'video_id': 'TEST_VIDEO_1',
            'language': 'en',
            'json_data': {
                'transcript': [
                    {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
                    {'text': 'This is a test', 'start': 2.0, 'duration': 2.5}
                ]
            },
            'markdown': '**0:00** Hello world\n\n**0:02** This is a test',
            'plain_text': 'Hello world This is a test'
        }

        # Test write
        print("   Writing transcript...")
        write_success = self.cache.save_transcript(
            'TEST_VIDEO_1',
            'Test Video 1',
            test_transcript
        )

        if not write_success:
            self.test_results['failed'].append('Transcript write failed')
            print("   ❌ Write failed")
            return False

        print("   ✅ Write successful")

        # Test read
        print("   Reading transcript...")
        cached_transcript = self.cache.get_transcript('TEST_VIDEO_1')

        if not cached_transcript:
            self.test_results['failed'].append('Transcript read failed')
            print("   ❌ Read failed")
            return False

        if cached_transcript.get('language') != 'en':
            self.test_results['failed'].append('Transcript data mismatch')
            print("   ❌ Data mismatch")
            return False

        transcript_entries = cached_transcript.get('json_data', {}).get('transcript', [])
        print(f"   ✅ Read successful: {len(transcript_entries)} entries")

        self.test_results['passed'].append('Transcript cache')
        return True

    def test_cache_statistics(self) -> bool:
        """Test cache statistics"""
        print("📊 Testing CACHE STATISTICS...")

        stats = self.cache.get_stats()

        if not stats.get('enabled'):
            self.test_results['failed'].append('Cache stats not available')
            print("   ❌ Stats not available")
            return False

        print(f"   Database: {stats.get('database')}")
        print(f"   Channels: {stats.get('channels_count', 0)}")
        print(f"   Videos: {stats.get('videos_count', 0)}")
        print(f"   Transcripts: {stats.get('transcripts_count', 0)}")

        self.test_results['passed'].append('Cache statistics')
        return True

    def test_timeseries_structure(self) -> bool:
        """Test that documents have proper time-series structure"""
        print("🔍 Testing TIME-SERIES STRUCTURE...")

        # Check a sample document from each collection
        for coll_name in ['channels', 'videos', 'transcripts']:
            sample = self.manager.get_sample_data(coll_name, limit=1)

            if sample:
                doc = sample[0]

                # Check required fields
                if 'timestamp' not in doc:
                    self.test_results['failed'].append(
                        f'{coll_name} missing timestamp field'
                    )
                    print(f"   ❌ {coll_name} missing timestamp")
                    return False

                if 'metadata' not in doc:
                    self.test_results['failed'].append(
                        f'{coll_name} missing metadata field'
                    )
                    print(f"   ❌ {coll_name} missing metadata")
                    return False

                if 'data' not in doc:
                    self.test_results['failed'].append(
                        f'{coll_name} missing data field'
                    )
                    print(f"   ❌ {coll_name} missing data")
                    return False

                print(f"   ✅ {coll_name} structure correct")

        self.test_results['passed'].append('Time-series structure')
        return True

    def cleanup(self):
        """Cleanup test data"""
        print()
        print("🧹 Cleaning up test data...")

        try:
            self.manager.db.channels.delete_many({'metadata.channel_id': 'TEST_CHANNEL_123'})
            self.manager.db.videos.delete_many({'metadata.channel_id': 'TEST_CHANNEL_123'})
            self.manager.db.transcripts.delete_many(
                {'metadata.video_id': {'$in': ['TEST_VIDEO_1', 'TEST_VIDEO_2']}}
            )
            print("   ✅ Test data cleaned up")
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {str(e)}")

    def print_results(self):
        """Print test results"""
        print()
        print("=" * 70)
        print("Test Results")
        print("=" * 70)
        print()

        if self.test_results['passed']:
            print(f"✅ Passed ({len(self.test_results['passed'])}):")
            for test in self.test_results['passed']:
                print(f"   - {test}")
            print()

        if self.test_results['failed']:
            print(f"❌ Failed ({len(self.test_results['failed'])}):")
            for test in self.test_results['failed']:
                print(f"   - {test}")
            print()

        if self.test_results['warnings']:
            print(f"⚠️  Warnings ({len(self.test_results['warnings'])}):")
            for warning in self.test_results['warnings']:
                print(f"   - {warning}")
            print()

        total_tests = len(self.test_results['passed']) + len(self.test_results['failed'])
        success_rate = (len(self.test_results['passed']) / total_tests * 100) if total_tests > 0 else 0

        print(f"Success Rate: {success_rate:.1f}% ({len(self.test_results['passed'])}/{total_tests})")
        print("=" * 70)

    def run_all_tests(self) -> bool:
        """Run all tests"""
        if not self.setup():
            return False

        try:
            # Run tests
            self.test_channel_cache()
            print()

            self.test_videos_cache()
            print()

            self.test_transcript_cache()
            print()

            self.test_cache_statistics()
            print()

            self.test_timeseries_structure()

            # Cleanup
            self.cleanup()

            # Print results
            self.print_results()

            # Return success if no failures
            return len(self.test_results['failed']) == 0

        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.cache:
                self.cache.close()
            if self.manager:
                self.manager.close()


def main():
    """Main entry point"""
    tester = MongoDBTester()

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)


if __name__ == '__main__':
    main()