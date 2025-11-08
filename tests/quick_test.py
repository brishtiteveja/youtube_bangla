"""
Quick test to verify the fix is working
Use a video that you know has transcripts
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from transcript_api import TranscriptProcessor

print("🧪 Quick Transcript Test")
print("=" * 70)

# Replace this with a video ID from your Pinaki Bhattacharya channel
# or any Bangla channel video you're testing
test_video_id = input("Enter a YouTube video ID to test (or press Enter to skip): ").strip()

if test_video_id:
    print(f"\n📹 Testing video: https://www.youtube.com/watch?v={test_video_id}")
    print("-" * 70)

    processor = TranscriptProcessor()

    result = processor.get_and_format(
        video_id=test_video_id,
        video_title="Test Video",
        languages=['bn', 'en', 'hi'],
        format_type='timestamped'
    )

    if result['success']:
        print("✅ SUCCESS!")
        print(f"\nLanguage: {result['metadata']['language_code']}")
        print(f"Entries: {result['metadata']['entry_count']}")
        print(f"Is Generated: {result['metadata']['is_generated']}")
        print(f"\nFirst 500 characters of transcript:\n")
        print(result['formatted_text'][:500])
        print("\n...")
        print("\n✅ The 'Get Transcript' button should work in Streamlit!")
    else:
        print(f"❌ FAILED: {result.get('error')}")
        print("\nNote: If you see IP blocking errors, wait a few minutes and try again.")
else:
    print("\nSkipped test. To test:")
    print("1. Find a YouTube video ID (the part after 'watch?v=' in the URL)")
    print("2. Run: python tests/quick_test.py")
    print("3. Paste the video ID when prompted")

print("\n" + "=" * 70)
print("Test complete! You can now run your Streamlit app with: streamlit run app.py")