"""
YouTube Transcript Collector
A modular application for collecting YouTube video transcripts
"""

from .config import Config
from .youtube_api import YouTubeAPIClient, ChannelManager
from .transcript_api import TranscriptFetcher, TranscriptFormatter, TranscriptProcessor
from .channel_database import ChannelDatabase

__version__ = '1.0.0'
__all__ = [
    'Config',
    'YouTubeAPIClient',
    'ChannelManager',
    'TranscriptFetcher',
    'TranscriptFormatter',
    'TranscriptProcessor',
    'ChannelDatabase'
]
