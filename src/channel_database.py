"""
Channel Database Module
Handles Bangladeshi channels database operations with categorization
"""

import json
import os
from typing import List, Dict, Optional


# Channel categories for Bangladeshi channels
CHANNEL_CATEGORIES = {
    'News': ['TV', 'News', 'Bangla News', 'Independent', 'Jamuna', 'Ekattor', 'ATN', 'DBC', 'BanglaVision', 'Dhruba', 'Channel', 'Times'],
    'Entertainment': ['Drama', 'Natok', 'Music', 'Movies', 'Films', 'Entertainment', 'Sangeeta', 'G Series', 'CD CHOICE'],
    'Education': ['School', 'Academy', 'Tutorial', 'Learn', '10 Minute', 'Brain Fix', 'Study'],
    'Kids': ['Kids', 'Children', 'Cartoon', 'Tonni', 'Maasranga Kids'],
    'Food': ['Food', 'Recipe', 'Cooking', 'SS FOOD'],
    'Gaming': ['Gaming', 'Gamer', 'Game', 'Potato Pseudo'],
    'Art & Craft': ['Art', 'Craft', 'Drawing', 'Farjana', 'Mukta'],
    'Lifestyle': ['Vlog', 'Lifestyle', 'Daily', 'Life'],
    'Technology': ['Tech', 'Technology', 'Gadget', 'Review'],
    'Comedy': ['Funny', 'Comedy', 'Fun', 'Laugh'],
    'Music': ['Music', 'Song', 'Bangla', 'Coke Studio', 'Holy Tune', 'Eagle'],
    'Religious': ['Islam', 'Religious', 'Quran', 'Holy'],
    'Sports': ['Sports', 'Cricket', 'Football'],
    'General': []  # Fallback category
}


class ChannelDatabase:
    """Manages the database of Bangladeshi YouTube channels with categorization"""

    def __init__(self, db_path: str = None):
        """
        Initialize ChannelDatabase

        Args:
            db_path: Path to the JSON database file
        """
        if db_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(
                os.path.dirname(current_dir),
                'data',
                'bangladeshi_channels.json'
            )

        self.db_path = db_path
        self.channels = self._load_database()

    def _load_database(self) -> List[Dict]:
        """
        Load channels from JSON file

        Returns:
            List of channel dictionaries
        """
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('channels', [])
        except FileNotFoundError:
            print(f"Warning: Database file not found at {self.db_path}")
            return []
        except Exception as e:
            print(f"Error loading database: {str(e)}")
            return []

    def get_all_channels(self) -> List[Dict]:
        """
        Get all channels

        Returns:
            List of all channel dictionaries
        """
        return self.channels

    def search_channels(self, query: str, limit: int = 100) -> List[Dict]:
        """
        Search channels by name

        Args:
            query: Search query (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching channel dictionaries
        """
        query_lower = query.lower()
        results = [
            ch for ch in self.channels
            if query_lower in ch['name'].lower()
        ]
        return results[:limit]

    def get_channel_by_rank(self, rank: int) -> Optional[Dict]:
        """
        Get channel by rank number

        Args:
            rank: Channel rank (1-1000)

        Returns:
            Channel dictionary or None
        """
        for channel in self.channels:
            if channel['rank'] == rank:
                return channel
        return None

    def get_top_channels(self, count: int = 50) -> List[Dict]:
        """
        Get top N channels by rank

        Args:
            count: Number of channels to return

        Returns:
            List of top channel dictionaries
        """
        sorted_channels = sorted(self.channels, key=lambda x: x['rank'])
        return sorted_channels[:count]

    def get_channel_names(self) -> List[str]:
        """
        Get list of all channel names

        Returns:
            List of channel names
        """
        return [ch['name'] for ch in self.channels]

    def format_for_display(self, channels: List[Dict] = None) -> List[str]:
        """
        Format channels for display in UI

        Args:
            channels: List of channels (default: all channels)

        Returns:
            List of formatted strings like "#1 - Channel Name"
        """
        if channels is None:
            channels = self.channels

        return [f"#{ch['rank']} - {ch['name']}" for ch in channels]

    def _categorize_channel(self, channel_name: str) -> str:
        """
        Determine category for a channel based on name

        Args:
            channel_name: Name of the channel

        Returns:
            Category name
        """
        for category, keywords in CHANNEL_CATEGORIES.items():
            if category == 'General':
                continue
            for keyword in keywords:
                if keyword.lower() in channel_name.lower():
                    return category
        return 'General'

    def get_channels_by_category(self, category: str, limit: int = None) -> List[Dict]:
        """
        Get channels in a specific category

        Args:
            category: Category name
            limit: Maximum number of channels (None for all)

        Returns:
            List of channel dictionaries with category added
        """
        categorized = []
        for channel in self.channels:
            ch_category = self._categorize_channel(channel['name'])
            if ch_category == category:
                channel_copy = channel.copy()
                channel_copy['category'] = ch_category
                categorized.append(channel_copy)

        if limit:
            return categorized[:limit]
        return categorized

    def get_all_categories(self) -> List[str]:
        """
        Get list of all available categories

        Returns:
            List of category names
        """
        return [cat for cat in CHANNEL_CATEGORIES.keys() if cat != 'General']

    def get_category_stats(self) -> Dict[str, int]:
        """
        Get count of channels per category

        Returns:
            Dictionary mapping category to count
        """
        stats = {cat: 0 for cat in CHANNEL_CATEGORIES.keys()}
        for channel in self.channels:
            category = self._categorize_channel(channel['name'])
            stats[category] += 1
        return stats

    def get_stats(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with stats
        """
        return {
            'total_channels': len(self.channels),
            'top_channel': self.channels[0] if self.channels else None,
            'categories': self.get_category_stats(),
            'database_path': self.db_path
        }
