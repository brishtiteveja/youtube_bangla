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
