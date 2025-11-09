"""
MongoDB Cache Module
Handles caching of channel data, videos, and transcripts in MongoDB
"""

import pymongo
from pymongo import MongoClient
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import Config


class MongoDBCache:
    """MongoDB cache for YouTube data"""

    def __init__(self):
        """Initialize MongoDB connection"""
        self.enabled = Config.USE_MONGODB_CACHE and Config.MONGODB_URI
        self.client = None
        self.db = None

        if self.enabled:
            try:
                self.client = MongoClient(
                    Config.MONGODB_URI,
                    serverSelectionTimeoutMS=5000
                )
                # Test connection
                self.client.server_info()
                self.db = self.client[Config.MONGODB_DATABASE]

                # Create time-series collections and indexes
                self._setup_collections()

                print(f"✅ MongoDB cache connected to {Config.MONGODB_DATABASE}")
            except Exception as e:
                print(f"⚠️ MongoDB connection failed: {str(e)}")
                self.enabled = False
                self.client = None
                self.db = None

    def _setup_collections(self):
        """Setup time-series collections and indexes"""
        if not self.enabled:
            return

        try:
            existing_collections = self.db.list_collection_names()

            # Create channels collection as time-series if it doesn't exist
            if 'channels' not in existing_collections:
                try:
                    self.db.create_collection(
                        'channels',
                        timeseries={
                            'timeField': 'timestamp',
                            'metaField': 'metadata',
                            'granularity': 'hours'
                        }
                    )
                    print("📊 Created time-series collection: channels")
                except Exception as e:
                    # Collection might already exist or not support time-series
                    print(f"Info: channels collection setup: {str(e)}")

            # Create videos collection as time-series if it doesn't exist
            if 'videos' not in existing_collections:
                try:
                    self.db.create_collection(
                        'videos',
                        timeseries={
                            'timeField': 'timestamp',
                            'metaField': 'metadata',
                            'granularity': 'hours'
                        }
                    )
                    print("📊 Created time-series collection: videos")
                except Exception as e:
                    print(f"Info: videos collection setup: {str(e)}")

            # Create transcripts collection as time-series if it doesn't exist
            if 'transcripts' not in existing_collections:
                try:
                    self.db.create_collection(
                        'transcripts',
                        timeseries={
                            'timeField': 'timestamp',
                            'metaField': 'metadata',
                            'granularity': 'hours'
                        }
                    )
                    print("📊 Created time-series collection: transcripts")
                except Exception as e:
                    print(f"Info: transcripts collection setup: {str(e)}")

            # Create indexes for efficient queries (on metadata fields for time-series)
            try:
                # For time-series collections, we index the metaField
                self.db.channels.create_index([("metadata.channel_id", 1)])
                self.db.channels.create_index([("metadata.channel_name", 1)])

                self.db.videos.create_index([("metadata.video_id", 1)])
                self.db.videos.create_index([("metadata.channel_id", 1)])

                self.db.transcripts.create_index([("metadata.video_id", 1)])

            except Exception as e:
                print(f"Info: Could not create all indexes: {str(e)}")

        except Exception as e:
            print(f"Warning: Could not setup collections: {str(e)}")

    # ==================== CHANNEL CACHING ====================

    def get_channel(self, channel_id: str = None, channel_name: str = None) -> Optional[Dict]:
        """
        Get cached channel data

        Args:
            channel_id: YouTube channel ID
            channel_name: Channel name

        Returns:
            Channel data dict or None
        """
        if not self.enabled:
            return None

        try:
            query = {}
            if channel_id:
                query['metadata.channel_id'] = channel_id
            elif channel_name:
                query['metadata.channel_name'] = channel_name
            else:
                return None

            # Check cache validity (7 days)
            cache_cutoff = datetime.utcnow() - timedelta(days=7)
            query['timestamp'] = {'$gte': cache_cutoff}

            # Sort by timestamp descending to get most recent
            result = self.db.channels.find_one(query, sort=[('timestamp', -1)])

            if result:
                print(f"✅ Cache hit: Channel {channel_id or channel_name}")
                return result.get('data')

            return None

        except Exception as e:
            print(f"Error reading channel cache: {str(e)}")
            return None

    def save_channel(self, channel_data: Dict) -> bool:
        """
        Save channel data to cache

        Args:
            channel_data: Channel information dictionary

        Returns:
            True if successful
        """
        if not self.enabled or not channel_data:
            return False

        try:
            channel_id = channel_data.get('channel_id')
            channel_name = channel_data.get('title')

            if not channel_id:
                return False

            # Time-series document structure
            doc = {
                'timestamp': datetime.utcnow(),  # Required timeField
                'metadata': {  # Required metaField
                    'channel_id': channel_id,
                    'channel_name': channel_name
                },
                'data': channel_data
            }

            # For time-series, we insert (MongoDB handles deduplication)
            self.db.channels.insert_one(doc)

            print(f"💾 Cached channel: {channel_name or channel_id}")
            return True

        except Exception as e:
            print(f"Error saving channel cache: {str(e)}")
            return False

    # ==================== VIDEO CACHING ====================

    def get_videos(self, channel_id: str, max_results: int = None) -> Optional[List[Dict]]:
        """
        Get cached videos for a channel

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to return

        Returns:
            List of video dicts or None
        """
        if not self.enabled:
            return None

        try:
            # Check cache validity (1 day for videos)
            cache_cutoff = datetime.utcnow() - timedelta(days=1)

            query = {
                'metadata.channel_id': channel_id,
                'timestamp': {'$gte': cache_cutoff}
            }

            cursor = self.db.videos.find(query).sort('timestamp', -1)

            if max_results:
                cursor = cursor.limit(max_results)

            videos = [doc['data'] for doc in cursor]

            if videos:
                print(f"✅ Cache hit: {len(videos)} videos for channel {channel_id}")
                return videos

            return None

        except Exception as e:
            print(f"Error reading videos cache: {str(e)}")
            return None

    def save_videos(self, channel_id: str, videos: List[Dict]) -> bool:
        """
        Save videos to cache

        Args:
            channel_id: YouTube channel ID
            videos: List of video dictionaries

        Returns:
            True if successful
        """
        if not self.enabled or not videos:
            return False

        try:
            timestamp = datetime.utcnow()

            for video in videos:
                video_id = video.get('video_id')
                if not video_id:
                    continue

                # Time-series document structure
                doc = {
                    'timestamp': timestamp,  # Required timeField
                    'metadata': {  # Required metaField
                        'video_id': video_id,
                        'channel_id': channel_id,
                        'published_at': video.get('published_at', '')
                    },
                    'data': video
                }

                # For time-series, we insert
                self.db.videos.insert_one(doc)

            print(f"💾 Cached {len(videos)} videos for channel {channel_id}")
            return True

        except Exception as e:
            print(f"Error saving videos cache: {str(e)}")
            return False

    # ==================== TRANSCRIPT CACHING ====================

    def get_transcript(self, video_id: str) -> Optional[Dict]:
        """
        Get cached transcript for a video

        Args:
            video_id: YouTube video ID

        Returns:
            Transcript data dict or None
        """
        if not self.enabled:
            return None

        try:
            # Transcripts don't expire (they rarely change)
            # Get the most recent transcript for this video
            result = self.db.transcripts.find_one(
                {'metadata.video_id': video_id},
                sort=[('timestamp', -1)]
            )

            if result:
                print(f"✅ Cache hit: Transcript for {video_id}")
                return result.get('data')

            return None

        except Exception as e:
            print(f"Error reading transcript cache: {str(e)}")
            return None

    def save_transcript(self, video_id: str, video_title: str, transcript_data: Dict) -> bool:
        """
        Save transcript to cache

        Args:
            video_id: YouTube video ID
            video_title: Video title
            transcript_data: Transcript data (result from transcript_processor)

        Returns:
            True if successful
        """
        if not self.enabled or not transcript_data:
            return False

        try:
            # Time-series document structure
            doc = {
                'timestamp': datetime.utcnow(),  # Required timeField
                'metadata': {  # Required metaField
                    'video_id': video_id,
                    'video_title': video_title
                },
                'data': transcript_data
            }

            # For time-series, we insert
            self.db.transcripts.insert_one(doc)

            print(f"💾 Cached transcript: {video_title}")
            return True

        except Exception as e:
            print(f"Error saving transcript cache: {str(e)}")
            return False

    # ==================== CACHE MANAGEMENT ====================

    def get_stats(self) -> Dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.enabled:
            return {'enabled': False}

        try:
            return {
                'enabled': True,
                'channels_count': self.db.channels.count_documents({}),
                'videos_count': self.db.videos.count_documents({}),
                'transcripts_count': self.db.transcripts.count_documents({}),
                'database': Config.MONGODB_DATABASE
            }
        except Exception as e:
            return {'enabled': True, 'error': str(e)}

    def clear_old_cache(self, days: int = 30):
        """
        Clear cache older than specified days

        Args:
            days: Age threshold in days
        """
        if not self.enabled:
            return

        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # For time-series collections, use timestamp field
            channels_deleted = self.db.channels.delete_many({'timestamp': {'$lt': cutoff}})
            videos_deleted = self.db.videos.delete_many({'timestamp': {'$lt': cutoff}})
            transcripts_deleted = self.db.transcripts.delete_many({'timestamp': {'$lt': cutoff}})

            print(f"🧹 Cleared old cache: {channels_deleted.deleted_count} channels, {videos_deleted.deleted_count} videos, {transcripts_deleted.deleted_count} transcripts")

        except Exception as e:
            print(f"Error clearing cache: {str(e)}")

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")