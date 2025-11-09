"""
YouTube Data API Module
Handles channel and video information fetching
"""

import requests
import time
from typing import List, Dict, Optional
import streamlit as st
from config import Config


class YouTubeAPIClient:
    """Client for YouTube Data API v3"""

    def __init__(self, api_key: str, use_proxy: bool = True, use_cache: bool = True):
        """
        Initialize YouTube API client

        Args:
            api_key: YouTube Data API key
            use_proxy: Whether to use proxy for API requests (helps avoid rate limiting)
            use_cache: Whether to use MongoDB cache
        """
        self.api_key = api_key
        self.base_url = 'https://www.googleapis.com/youtube/v3'
        self.use_proxy = use_proxy and Config.USE_PROXY
        self.use_cache = use_cache

        # Initialize cache
        self.cache = None
        if self.use_cache:
            try:
                from mongodb_cache import MongoDBCache
                self.cache = MongoDBCache()
            except Exception as e:
                print(f"Warning: Could not initialize cache: {str(e)}")
                self.cache = None

    def _make_request(self, url: str, params: dict, max_retries: int = 3) -> Optional[dict]:
        """
        Make API request with optional proxy support and retry logic

        Args:
            url: API endpoint URL
            params: Query parameters
            max_retries: Maximum number of retry attempts

        Returns:
            JSON response or None on failure
        """
        for attempt in range(max_retries):
            try:
                # Get proxy configuration if enabled
                proxies = None
                if self.use_proxy:
                    proxies = Config.get_proxy_dict()
                    if proxies:
                        # Remove the extra metadata keys that Config.get_proxy_dict() adds
                        proxies = {k: v for k, v in proxies.items() if k in ['http', 'https']}

                # Make request with timeout
                response = requests.get(
                    url,
                    params=params,
                    proxies=proxies,
                    timeout=10
                )

                # Check if successful
                if response.status_code == 200:
                    return response.json()

                # Handle rate limiting
                elif response.status_code == 403:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', 'Unknown error')
                        print(f"YouTube API Error 403: {error_msg}")

                        # If quota exceeded, don't retry
                        if 'quota' in error_msg.lower():
                            print("API quota exceeded. Please wait or use a different API key.")
                            return None

                    # Rate limit - wait and retry with different proxy
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue

                # Other errors
                else:
                    print(f"API request failed with status {response.status_code}: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue

                return None

            except requests.exceptions.RequestException as e:
                print(f"Request exception (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return None

        return None

    def search_channels(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for YouTube channels by keyword

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of channel dictionaries
        """
        url = f'{self.base_url}/search'
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'channel',
            'maxResults': max_results,
            'key': self.api_key
        }

        data = self._make_request(url, params)

        if data and 'items' in data:
            channels = []
            for item in data['items']:
                channels.append({
                    'title': item['snippet']['channelTitle'],
                    'channel_id': item['snippet']['channelId'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url']
                })
            return channels

        return []

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get detailed channel information

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dictionary with channel information or None
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get_channel(channel_id=channel_id)
            if cached:
                return cached

        # Fetch from API
        url = f'{self.base_url}/channels'
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': channel_id,
            'key': self.api_key
        }

        data = self._make_request(url, params)

        if data and 'items' in data and len(data['items']) > 0:
            item = data['items'][0]
            channel_info = {
                'title': item['snippet']['title'],
                'channel_id': channel_id,
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
                'subscriber_count': item['statistics'].get('subscriberCount', 'N/A'),
                'video_count': item['statistics'].get('videoCount', 'N/A'),
                'uploads_playlist': item['contentDetails']['relatedPlaylists']['uploads']
            }

            # Save to cache
            if self.cache:
                self.cache.save_channel(channel_info)

            return channel_info

        return None

    def get_channel_videos(
        self,
        channel_id: str,
        max_results: int = 50,
        show_progress: bool = True
    ) -> List[Dict]:
        """
        Get videos from a channel

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch
            show_progress: Show progress bar (for Streamlit)

        Returns:
            List of video dictionaries
        """
        # Check cache first
        if self.cache:
            cached_videos = self.cache.get_videos(channel_id, max_results)
            if cached_videos:
                return cached_videos

        # First get the uploads playlist
        channel_info = self.get_channel_info(channel_id)
        if not channel_info:
            return []

        uploads_playlist_id = channel_info['uploads_playlist']
        videos = []
        url = f'{self.base_url}/playlistItems'
        next_page_token = None

        # Progress tracking
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()

        while len(videos) < max_results:
            params = {
                'part': 'snippet',
                'playlistId': uploads_playlist_id,
                'maxResults': min(50, max_results - len(videos)),
                'key': self.api_key
            }

            if next_page_token:
                params['pageToken'] = next_page_token

            data = self._make_request(url, params)

            if not data or 'items' not in data:
                break

            for item in data['items']:
                videos.append({
                    'video_id': item['snippet']['resourceId']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200] + '...',
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url']
                })

            if show_progress:
                progress = len(videos) / max_results
                progress_bar.progress(min(progress, 1.0))
                status_text.text(f"Loading videos... {len(videos)}/{max_results}")

            if 'nextPageToken' not in data or len(videos) >= max_results:
                break

            next_page_token = data['nextPageToken']
            time.sleep(0.3)  # Rate limiting

        if show_progress:
            progress_bar.empty()
            status_text.empty()

        # Save to cache
        if self.cache and videos:
            self.cache.save_videos(channel_id, videos)

        return videos

    def get_video_statistics(self, video_ids: List[str]) -> Dict[str, Dict]:
        """
        Get statistics for multiple videos (views, likes, comments)

        Args:
            video_ids: List of video IDs (max 50 per request)

        Returns:
            Dictionary mapping video_id to stats
        """
        if not video_ids:
            return {}

        stats = {}
        # YouTube API allows max 50 IDs per request
        batch_size = 50

        for i in range(0, len(video_ids), batch_size):
            batch = video_ids[i:i+batch_size]
            video_ids_str = ','.join(batch)

            url = f'{self.base_url}/videos'
            params = {
                'part': 'statistics',
                'id': video_ids_str,
                'key': self.api_key
            }

            data = self._make_request(url, params)

            if data and 'items' in data:
                for item in data['items']:
                    video_id = item['id']
                    stats_data = item['statistics']

                    stats[video_id] = {
                        'view_count': int(stats_data.get('viewCount', 0)),
                        'like_count': int(stats_data.get('likeCount', 0)),
                        'comment_count': int(stats_data.get('commentCount', 0))
                    }

            time.sleep(0.3)  # Rate limiting

        return stats

    def enrich_videos_with_stats(self, videos: List[Dict]) -> List[Dict]:
        """
        Add statistics to video dictionaries

        Args:
            videos: List of video dictionaries

        Returns:
            List of enriched video dictionaries with stats
        """
        if not videos:
            return videos

        # Extract video IDs
        video_ids = [v['video_id'] for v in videos]

        # Get statistics
        stats = self.get_video_statistics(video_ids)

        # Enrich videos with stats
        enriched_videos = []
        for video in videos:
            video_copy = video.copy()
            video_id = video['video_id']

            if video_id in stats:
                video_copy.update(stats[video_id])
            else:
                # Default values if stats not available
                video_copy['view_count'] = 0
                video_copy['like_count'] = 0
                video_copy['comment_count'] = 0

            enriched_videos.append(video_copy)

        return enriched_videos


class ChannelManager:
    """High-level channel management operations"""

    def __init__(self, api_client: YouTubeAPIClient):
        """
        Initialize ChannelManager

        Args:
            api_client: YouTubeAPIClient instance
        """
        self.api_client = api_client

    def get_channel_by_url(self, channel_url: str) -> Optional[Dict]:
        """
        Extract channel info from channel URL

        Args:
            channel_url: YouTube channel URL

        Returns:
            Channel info dictionary or None
        """
        try:
            # Handle @username format
            if '@' in channel_url:
                username = channel_url.split('@')[-1].strip()
                channels = self.api_client.search_channels(username, max_results=5)
                if channels:
                    return channels[0]  # Return best match

            # Handle channel ID format
            elif 'channel/' in channel_url:
                channel_id = channel_url.split('channel/')[-1].strip()
                return self.api_client.get_channel_info(channel_id)

            return None
        except Exception as e:
            print(f"Error parsing channel URL: {str(e)}")
            return None

    def search_and_select(self, query: str, auto_select: bool = True) -> Optional[Dict]:
        """
        Search for channel and optionally auto-select first result

        Args:
            query: Search query
            auto_select: Auto-select first result

        Returns:
            Channel info or None
        """
        channels = self.api_client.search_channels(query, max_results=5)

        if not channels:
            return None

        if auto_select:
            # Get full info for first result
            return self.api_client.get_channel_info(channels[0]['channel_id'])

        return channels
