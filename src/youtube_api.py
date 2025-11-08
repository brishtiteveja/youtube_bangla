"""
YouTube Data API Module
Handles channel and video information fetching
"""

import requests
import time
from typing import List, Dict, Optional
import streamlit as st


class YouTubeAPIClient:
    """Client for YouTube Data API v3"""

    def __init__(self, api_key: str):
        """
        Initialize YouTube API client

        Args:
            api_key: YouTube Data API key
        """
        self.api_key = api_key
        self.base_url = 'https://www.googleapis.com/youtube/v3'

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

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if 'items' in data:
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
        except Exception as e:
            print(f"Error searching channels: {str(e)}")
            return []

    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get detailed channel information

        Args:
            channel_id: YouTube channel ID

        Returns:
            Dictionary with channel information or None
        """
        url = f'{self.base_url}/channels'
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': channel_id,
            'key': self.api_key
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                return {
                    'title': item['snippet']['title'],
                    'channel_id': channel_id,
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'subscriber_count': item['statistics'].get('subscriberCount', 'N/A'),
                    'video_count': item['statistics'].get('videoCount', 'N/A'),
                    'uploads_playlist': item['contentDetails']['relatedPlaylists']['uploads']
                }
            return None
        except Exception as e:
            print(f"Error getting channel info: {str(e)}")
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

            try:
                response = requests.get(url, params=params)
                data = response.json()

                if 'items' not in data:
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

            except Exception as e:
                print(f"Error loading videos: {str(e)}")
                break

        if show_progress:
            progress_bar.empty()
            status_text.empty()

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

            try:
                response = requests.get(url, params=params)
                data = response.json()

                if 'items' in data:
                    for item in data['items']:
                        video_id = item['id']
                        stats_data = item['statistics']

                        stats[video_id] = {
                            'view_count': int(stats_data.get('viewCount', 0)),
                            'like_count': int(stats_data.get('likeCount', 0)),
                            'comment_count': int(stats_data.get('commentCount', 0))
                        }

                time.sleep(0.3)  # Rate limiting

            except Exception as e:
                print(f"Error fetching video statistics: {str(e)}")
                continue

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
