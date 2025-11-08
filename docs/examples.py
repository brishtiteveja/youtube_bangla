"""
Example Scripts for YouTube Transcript Collector
Run these with: uv run python docs/examples.py
"""

import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from youtube_api import YouTubeAPIClient, ChannelManager
from transcript_api import TranscriptProcessor
from channel_database import ChannelDatabase
from config import Config


def example_1_simple_transcript():
    """Example 1: Get transcript for a single video"""
    print("\n" + "="*60)
    print("Example 1: Get Single Video Transcript")
    print("="*60 + "\n")

    processor = TranscriptProcessor()

    # Pinaki Bhattacharya video
    video_id = "m4ri2oiiKik"

    print(f"Fetching transcript for video: {video_id}")

    result = processor.get_and_format(
        video_id=video_id,
        video_title="Political Commentary",
        languages=['bn'],
        format_type='timestamped'
    )

    if result['success']:
        print("✅ Success!")
        print(f"Language: {result['metadata']['language_code']}")
        print(f"Entries: {result['metadata']['entry_count']}")
        print(f"\nFirst 500 characters:")
        print(result['formatted_text'][:500])
    else:
        print(f"❌ Error: {result['error']}")


def example_2_search_channel():
    """Example 2: Search for a channel and get info"""
    print("\n" + "="*60)
    print("Example 2: Search Channel")
    print("="*60 + "\n")

    api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)

    channel_name = "Pinaki Bhattacharya"
    print(f"Searching for: {channel_name}")

    channels = api_client.search_channels(channel_name, max_results=3)

    if channels:
        print(f"✅ Found {len(channels)} results:\n")
        for idx, channel in enumerate(channels, 1):
            print(f"{idx}. {channel['title']}")
            print(f"   ID: {channel['channel_id']}")
            print(f"   Description: {channel['description'][:80]}...")
            print()
    else:
        print("❌ No channels found")


def example_3_get_channel_videos():
    """Example 3: Get videos from a channel"""
    print("\n" + "="*60)
    print("Example 3: Get Channel Videos")
    print("="*60 + "\n")

    api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)

    # First search for channel
    channels = api_client.search_channels("Pinaki Bhattacharya", max_results=1)

    if not channels:
        print("❌ Channel not found")
        return

    channel_id = channels[0]['channel_id']
    print(f"Channel: {channels[0]['title']}")
    print(f"Getting videos...\n")

    # Get videos
    videos = api_client.get_channel_videos(
        channel_id,
        max_results=10,
        show_progress=False
    )

    if videos:
        print(f"✅ Found {len(videos)} videos:\n")
        for idx, video in enumerate(videos, 1):
            print(f"{idx}. {video['title']}")
            print(f"   ID: {video['video_id']}")
            print(f"   Published: {video['published_at'][:10]}")
            print()
    else:
        print("❌ No videos found")


def example_4_bd_channels_database():
    """Example 4: Use Bangladeshi channels database"""
    print("\n" + "="*60)
    print("Example 4: BD Channels Database")
    print("="*60 + "\n")

    db = ChannelDatabase()

    # Get stats
    stats = db.get_stats()
    print(f"Database Stats:")
    print(f"Total Channels: {stats['total_channels']}")
    print(f"Database Path: {stats['database_path']}")
    print()

    # Get top 10
    print("Top 10 BD Channels:")
    top_10 = db.get_top_channels(10)
    for channel in top_10:
        print(f"  #{channel['rank']} - {channel['name']}")
    print()

    # Search channels
    print("Search results for 'news':")
    news_channels = db.search_channels("news", limit=5)
    for channel in news_channels:
        print(f"  #{channel['rank']} - {channel['name']}")


def example_5_batch_download():
    """Example 5: Batch download transcripts from a channel"""
    print("\n" + "="*60)
    print("Example 5: Batch Download Transcripts")
    print("="*60 + "\n")

    api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)
    processor = TranscriptProcessor()

    # Search channel
    channels = api_client.search_channels("Pinaki Bhattacharya", max_results=1)

    if not channels:
        print("❌ Channel not found")
        return

    channel_id = channels[0]['channel_id']
    print(f"Channel: {channels[0]['title']}")
    print("Getting videos...\n")

    # Get videos
    videos = api_client.get_channel_videos(
        channel_id,
        max_results=5,  # Only 5 for demo
        show_progress=False
    )

    if not videos:
        print("❌ No videos found")
        return

    print(f"Found {len(videos)} videos")
    print("Downloading transcripts...\n")

    # Process each video
    success_count = 0
    for idx, video in enumerate(videos, 1):
        print(f"{idx}. {video['title'][:60]}...")

        result = processor.get_and_format(
            video['video_id'],
            video['title'],
            languages=['bn', 'en'],
            format_type='timestamped'
        )

        if result['success']:
            # Save to output directory
            output_dir = Config.OUTPUT_DIR
            os.makedirs(output_dir, exist_ok=True)

            # Save JSON
            json_path = os.path.join(output_dir, f"{video['video_id']}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result['json_data'], f, ensure_ascii=False, indent=2)

            # Save TXT
            txt_path = os.path.join(output_dir, f"{video['video_id']}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(result['formatted_text'])

            print(f"   ✅ Saved ({result['metadata']['language_code']})")
            success_count += 1
        else:
            print(f"   ❌ {result['error']}")

        print()

    print(f"\nComplete! Downloaded {success_count}/{len(videos)} transcripts")
    print(f"Files saved to: {Config.OUTPUT_DIR}")


def example_6_channel_by_url():
    """Example 6: Load channel by URL"""
    print("\n" + "="*60)
    print("Example 6: Load Channel by URL")
    print("="*60 + "\n")

    api_client = YouTubeAPIClient(Config.YOUTUBE_API_KEY)
    manager = ChannelManager(api_client)

    url = "https://www.youtube.com/@PinakiBhattacharya"
    print(f"Loading channel from URL: {url}\n")

    result = manager.get_channel_by_url(url)

    if result:
        channel = api_client.get_channel_info(result['channel_id'])
        if channel:
            print("✅ Channel loaded!")
            print(f"Title: {channel['title']}")
            print(f"ID: {channel['channel_id']}")
            print(f"Videos: {channel['video_count']}")
            print(f"Subscribers: {channel['subscriber_count']}")
    else:
        print("❌ Could not load channel")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("YouTube Transcript Collector - Examples")
    print("="*60)

    examples = [
        ("1", "Simple Transcript", example_1_simple_transcript),
        ("2", "Search Channel", example_2_search_channel),
        ("3", "Get Channel Videos", example_3_get_channel_videos),
        ("4", "BD Channels Database", example_4_bd_channels_database),
        ("5", "Batch Download", example_5_batch_download),
        ("6", "Channel by URL", example_6_channel_by_url),
    ]

    print("\nAvailable Examples:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")
    print("  all. Run all examples")
    print("  q. Quit")

    choice = input("\nSelect example (1-6, all, q): ").strip().lower()

    if choice == 'q':
        return

    if choice == 'all':
        for _, _, func in examples:
            func()
            input("\nPress Enter to continue...")
    else:
        for num, name, func in examples:
            if choice == num:
                func()
                break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
