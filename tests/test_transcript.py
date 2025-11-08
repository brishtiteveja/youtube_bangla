"""
Test script to debug transcript fetching
"""

import sys
import os

# Add src to path (go up one level from tests/)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from transcript_api import TranscriptProcessor, TranscriptFetcher

# Test with a known video that should have transcripts
# Using a popular video ID (you can replace with actual video from your channel)
test_video_ids = [
    "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up (should have English)
    "9bZkp7q19f0",  # Gangnam Style (should have subtitles)
]

print("=" * 70)
print("TESTING TRANSCRIPT FETCHER")
print("=" * 70)

fetcher = TranscriptFetcher()

for video_id in test_video_ids:
    print(f"\n📹 Testing video ID: {video_id}")
    print("-" * 70)

    # Test 1: Try with default languages (bn, en, hi)
    print("Test 1: Default languages ['bn', 'en', 'hi']")
    result = fetcher.get_transcript(video_id, languages=['bn', 'en', 'hi'])
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Language: {result['language_code']}")
        print(f"  Is Generated: {result['is_generated']}")
        print(f"  Entries: {len(result['transcript'])}")
        print(f"  First entry: {result['transcript'][0]}")
    else:
        print(f"  Error: {result.get('error')}")

    # Test 2: Try with just English
    print("\nTest 2: Just English ['en']")
    result = fetcher.get_transcript(video_id, languages=['en'])
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Language: {result['language_code']}")
        print(f"  Entries: {len(result['transcript'])}")
    else:
        print(f"  Error: {result.get('error')}")

    # Test 3: Try with no language specified (auto-detect)
    print("\nTest 3: No language specified (auto-detect)")
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id)
        transcript = [
            {'text': s.text, 'start': s.start, 'duration': s.duration}
            for s in transcript_data
        ]
        print(f"  Success: True")
        print(f"  Entries: {len(transcript)}")
        print(f"  First entry: {transcript[0]}")
    except Exception as e:
        print(f"  Error: {str(e)}")

print("\n" + "=" * 70)
print("TESTING TRANSCRIPT PROCESSOR")
print("=" * 70)

processor = TranscriptProcessor()

for video_id in test_video_ids:
    print(f"\n📹 Testing video ID: {video_id}")
    print("-" * 70)

    result = processor.get_and_format(
        video_id=video_id,
        video_title="Test Video",
        languages=['bn', 'en', 'hi'],
        format_type='timestamped'
    )

    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Language: {result['metadata']['language_code']}")
        print(f"  Entry Count: {result['metadata']['entry_count']}")
        print(f"  First 200 chars of formatted text:")
        print(f"  {result['formatted_text'][:200]}...")
    else:
        print(f"  Error: {result.get('error')}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
