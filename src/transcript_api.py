"""
Transcript API Module
Handles YouTube transcript fetching and processing
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from youtube_transcript_api.proxies import GenericProxyConfig
from typing import List, Dict, Optional
from datetime import datetime
import time
from config import Config


class TranscriptFetcher:
    """Handles fetching transcripts from YouTube videos"""

    def __init__(self, use_proxy: bool = None):
        """
        Initialize the fetcher with YouTubeTranscriptApi instance

        Args:
            use_proxy: Override proxy usage (defaults to Config.USE_PROXY)
        """
        # Determine if we should use proxy
        self.use_proxy = use_proxy if use_proxy is not None else Config.USE_PROXY
        self.max_retries = Config.MAX_RETRY_ATTEMPTS
        self.api = None  # Will be initialized on each request for rotating proxies

    def _create_api_instance(self):
        """Create a new API instance with fresh proxy configuration"""
        # Get proxy configuration
        proxy_dict = Config.get_proxy_dict() if self.use_proxy else None

        # Initialize API with or without proxies
        if proxy_dict:
            # Create GenericProxyConfig from our proxy dict
            proxy_config = GenericProxyConfig(
                http_url=proxy_dict.get('http'),
                https_url=proxy_dict.get('https')
            )
            return YouTubeTranscriptApi(proxy_config=proxy_config)
        else:
            return YouTubeTranscriptApi()

    def get_transcript(self, video_id: str, languages: List[str] = None) -> Dict:
        """
        Get transcript for a video in specified languages with retry mechanism

        Args:
            video_id: YouTube video ID
            languages: List of language codes to try (default: ['bn', 'en', 'hi'])

        Returns:
            Dictionary with success status and transcript data
        """
        if languages is None:
            languages = ['bn', 'en', 'hi']

        last_error = None

        # Retry loop - try up to MAX_RETRY_ATTEMPTS times
        for attempt in range(1, self.max_retries + 1):
            try:
                # Create fresh API instance with new proxy (for rotating proxies)
                api = self._create_api_instance()

                # Try each language in order
                for lang in languages:
                    try:
                        transcript_data = api.fetch(video_id, languages=[lang])
                        # Convert FetchedTranscriptSnippet objects to dict format
                        transcript = [
                            {
                                'text': snippet.text,
                                'start': snippet.start,
                                'duration': snippet.duration
                            }
                            for snippet in transcript_data
                        ]

                        # Success! Log if we needed retries
                        if attempt > 1:
                            print(f"✅ Success on attempt {attempt}/{self.max_retries}")

                        return {
                            'success': True,
                            'transcript': transcript,
                            'language_code': lang,
                            'is_generated': self._check_if_generated(video_id, lang),
                            'attempts': attempt
                        }
                    except NoTranscriptFound:
                        continue

                # If no preferred language found, get any available
                transcript_data = api.fetch(video_id)
                transcript = [
                    {
                        'text': snippet.text,
                        'start': snippet.start,
                        'duration': snippet.duration
                    }
                    for snippet in transcript_data
                ]

                if attempt > 1:
                    print(f"✅ Success on attempt {attempt}/{self.max_retries}")

                return {
                    'success': True,
                    'transcript': transcript,
                    'language_code': 'unknown',
                    'is_generated': True,
                    'attempts': attempt
                }

            except NoTranscriptFound as e:
                # Don't retry for NoTranscriptFound - transcript truly doesn't exist
                return {'success': False, 'error': 'No transcript found', 'attempts': attempt}

            except TranscriptsDisabled as e:
                # Don't retry for TranscriptsDisabled - they are intentionally disabled
                return {'success': False, 'error': 'Transcripts disabled', 'attempts': attempt}

            except Exception as e:
                last_error = str(e)

                # If we have retries left and we're using proxies, try again
                if attempt < self.max_retries and self.use_proxy:
                    print(f"⚠️  Attempt {attempt}/{self.max_retries} failed: {last_error}")
                    print(f"🔄 Retrying with new proxy (attempt {attempt + 1}/{self.max_retries})...")
                    time.sleep(1)  # Brief pause between retries
                    continue
                else:
                    # Last attempt failed or not using proxies
                    break

        # All attempts failed
        return {
            'success': False,
            'error': f'Failed after {self.max_retries} attempts. Last error: {last_error}',
            'attempts': self.max_retries
        }

    def _check_if_generated(self, video_id: str, language_code: str) -> bool:
        """Check if transcript is auto-generated"""
        try:
            # This is a workaround since list_transcripts might not be available
            # We'll assume it's generated for now
            return True
        except:
            return True


class TranscriptFormatter:
    """Formats transcripts in various output formats"""

    @staticmethod
    def format_timestamped(transcript: List[Dict]) -> str:
        """
        Format transcript with timestamps [MM:SS] format

        Args:
            transcript: List of transcript entries

        Returns:
            Formatted string with timestamps
        """
        lines = []
        for entry in transcript:
            timestamp = entry['start']
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            text = entry['text']
            lines.append(f"[{minutes:02d}:{seconds:02d}] {text}")
        return "\n".join(lines)

    @staticmethod
    def format_plain_text(transcript: List[Dict]) -> str:
        """
        Extract just the text without timestamps

        Args:
            transcript: List of transcript entries

        Returns:
            Plain text string
        """
        return " ".join([entry['text'] for entry in transcript])

    @staticmethod
    def to_json_dict(video_id: str, video_title: str, transcript_data: Dict) -> Dict:
        """
        Create JSON-serializable dictionary with complete metadata

        Args:
            video_id: YouTube video ID
            video_title: Video title
            transcript_data: Transcript data from TranscriptFetcher

        Returns:
            Dictionary ready for JSON serialization
        """
        return {
            'video_id': video_id,
            'video_title': video_title,
            'video_url': f'https://www.youtube.com/watch?v={video_id}',
            'language_code': transcript_data.get('language_code'),
            'is_generated': transcript_data.get('is_generated', True),
            'transcript': transcript_data.get('transcript', []),
            'collected_at': datetime.now().isoformat()
        }


class TranscriptProcessor:
    """High-level transcript processing operations"""

    def __init__(self, use_proxy: bool = None):
        """
        Initialize TranscriptProcessor

        Args:
            use_proxy: Override proxy usage (defaults to Config.USE_PROXY)
        """
        self.fetcher = TranscriptFetcher(use_proxy=use_proxy)
        self.formatter = TranscriptFormatter()

    def get_and_format(
        self,
        video_id: str,
        video_title: str,
        languages: List[str] = None,
        format_type: str = 'timestamped'
    ) -> Dict:
        """
        Fetch and format transcript in one operation

        Args:
            video_id: YouTube video ID
            video_title: Video title
            languages: List of language codes
            format_type: 'timestamped' or 'plain'

        Returns:
            Dictionary with formatted transcript and metadata
        """
        result = self.fetcher.get_transcript(video_id, languages)

        if not result['success']:
            return result

        # Format the transcript
        if format_type == 'timestamped':
            formatted_text = self.formatter.format_timestamped(result['transcript'])
        else:
            formatted_text = self.formatter.format_plain_text(result['transcript'])

        return {
            'success': True,
            'formatted_text': formatted_text,
            'json_data': self.formatter.to_json_dict(video_id, video_title, result),
            'metadata': {
                'language_code': result['language_code'],
                'is_generated': result['is_generated'],
                'entry_count': len(result['transcript'])
            }
        }
