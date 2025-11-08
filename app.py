"""
YouTube Transcript Collector - Main Streamlit Application
Clean, modular, and well-organized
"""

import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import Config
from youtube_api import YouTubeAPIClient, ChannelManager
from transcript_api import TranscriptProcessor
from channel_database import ChannelDatabase

# Ensure directories exist
Config.ensure_directories()

# Page configuration
st.set_page_config(
    page_title=Config.PAGE_TITLE,
    page_icon=Config.PAGE_ICON,
    layout=Config.LAYOUT
)

# Initialize session state
if 'channel_data' not in st.session_state:
    st.session_state.channel_data = None
if 'videos' not in st.session_state:
    st.session_state.videos = []
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = {}

# Initialize components
@st.cache_resource
def get_api_client():
    """Get cached YouTube API client"""
    return YouTubeAPIClient(Config.YOUTUBE_API_KEY)

@st.cache_resource
def get_channel_manager():
    """Get cached channel manager"""
    return ChannelManager(get_api_client())

@st.cache_resource
def get_transcript_processor():
    """Get cached transcript processor"""
    return TranscriptProcessor()

@st.cache_data
def get_channel_database():
    """Get cached channel database"""
    return ChannelDatabase()

# Get instances
api_client = get_api_client()
channel_manager = get_channel_manager()
transcript_processor = get_transcript_processor()
db = get_channel_database()


def load_channel(channel_name: str):
    """Load a channel by name"""
    with st.spinner(f"Loading {channel_name}..."):
        result = channel_manager.search_and_select(channel_name, auto_select=True)
        if result:
            st.session_state.channel_data = result
            st.session_state.videos = []
            st.session_state.transcripts = {}
            st.success(f"✅ Loaded {channel_name}!")
            st.rerun()
        else:
            st.error("Channel not found")


# App UI
st.title(f"{Config.PAGE_ICON} YouTube Transcript Collector - Bangladesh")
st.markdown("Browse 1000+ Bangladeshi channels, search any YouTube channel, and download transcripts")

# Sidebar for channel selection
with st.sidebar:
    st.header("📺 Select Channel")

    # Tab selection
    tab_method = st.radio(
        "Choose method:",
        ["🇧🇩 Bangladeshi Channels", "🔍 Search Any Channel", "🔗 Channel URL"],
        index=0
    )

    if tab_method == "🇧🇩 Bangladeshi Channels":
        st.subheader("Top 1000 BD Channels")

        # Default channel button
        if st.button(
            f"⭐ Load Default: {Config.DEFAULT_CHANNEL}",
            type="primary",
            use_container_width=True
        ):
            load_channel(Config.DEFAULT_CHANNEL)

        st.divider()

        # Search within BD channels
        search_bd = st.text_input("🔍 Filter BD channels:", placeholder="Type to filter...")

        # Filter channels
        if search_bd:
            filtered_channels = db.search_channels(search_bd, limit=100)
        else:
            filtered_channels = db.get_top_channels(100)

        st.caption(f"Showing {len(filtered_channels)} channels")

        # Display as selectbox
        if filtered_channels:
            channel_options = db.format_for_display(filtered_channels)
            selected_option = st.selectbox(
                "Select a channel:",
                [""] + channel_options,
                key="bd_channel_select"
            )

            if selected_option and selected_option != "":
                # Extract channel name
                selected_name = selected_option.split(" - ", 1)[1]

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{selected_name}**")
                with col2:
                    if st.button("Load", key=f"load_{selected_name}"):
                        load_channel(selected_name)

    elif tab_method == "🔍 Search Any Channel":
        search_query = st.text_input("Enter channel name:", placeholder="e.g., BBC News")

        if st.button("Search", type="primary", use_container_width=True):
            if search_query:
                with st.spinner("Searching..."):
                    channels = api_client.search_channels(search_query, max_results=10)
                    if channels:
                        st.session_state.search_results = channels
                    else:
                        st.warning("No channels found")

        if 'search_results' in st.session_state:
            st.subheader("Search Results")
            for idx, channel in enumerate(st.session_state.search_results):
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(channel['thumbnail'], width=60)
                    with col2:
                        if st.button(
                            channel['title'],
                            key=f"search_{idx}",
                            use_container_width=True
                        ):
                            st.session_state.channel_data = api_client.get_channel_info(
                                channel['channel_id']
                            )
                            st.session_state.videos = []
                            st.session_state.transcripts = {}
                            st.rerun()
                    st.caption(channel['description'][:80] + "...")
                    st.divider()

    else:  # Channel URL
        channel_url = st.text_input(
            "Paste channel URL:",
            placeholder="https://www.youtube.com/@ChannelName"
        )

        if st.button("Load Channel", type="primary", use_container_width=True):
            if channel_url:
                with st.spinner("Loading channel..."):
                    result = channel_manager.get_channel_by_url(channel_url)
                    if result:
                        st.session_state.channel_data = api_client.get_channel_info(
                            result['channel_id']
                        )
                        st.session_state.videos = []
                        st.session_state.transcripts = {}
                        st.success("✅ Channel loaded!")
                        st.rerun()
                    else:
                        st.error("Channel not found")

# Main content area
if st.session_state.channel_data:
    channel = st.session_state.channel_data

    # Channel header
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(channel['thumbnail'], width=100)
    with col2:
        st.header(channel['title'])
        st.caption(
            f"📺 {channel['video_count']} videos | "
            f"👥 {channel['subscriber_count']} subscribers"
        )
        if channel['description']:
            with st.expander("📄 Channel Description"):
                st.write(channel['description'][:500] + "...")

    st.divider()

    # Load videos section
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        max_videos = st.number_input(
            "Videos to load:",
            min_value=Config.MIN_VIDEO_COUNT,
            max_value=Config.MAX_VIDEO_COUNT,
            value=Config.DEFAULT_VIDEO_COUNT,
            step=10
        )
    with col2:
        st.write("")
        if st.button("📹 Load Videos", type="primary", use_container_width=True):
            with st.spinner(f"Loading up to {max_videos} videos..."):
                st.session_state.videos = api_client.get_channel_videos(
                    channel['channel_id'],
                    max_results=max_videos
                )
                st.success(f"✅ Loaded {len(st.session_state.videos)} videos!")
                st.rerun()

    # Display videos
    if st.session_state.videos:
        st.subheader(f"📹 Videos ({len(st.session_state.videos)})")

        # Controls
        col1, col2 = st.columns([2, 2])
        with col1:
            selected_lang = st.selectbox(
                "🌍 Preferred language:",
                list(Config.LANGUAGE_OPTIONS.keys())
            )
            preferred_languages = (
                [Config.LANGUAGE_OPTIONS[selected_lang]]
                if Config.LANGUAGE_OPTIONS[selected_lang] != 'auto'
                else Config.DEFAULT_LANGUAGES
            )

        with col2:
            search_filter = st.text_input("🔍 Filter videos:", "")

        # Filter videos
        filtered_videos = st.session_state.videos
        if search_filter:
            filtered_videos = [
                v for v in st.session_state.videos
                if search_filter.lower() in v['title'].lower()
            ]

        st.caption(f"Showing {len(filtered_videos)} of {len(st.session_state.videos)} videos")

        # Display videos
        for idx, video in enumerate(filtered_videos):
            with st.expander(f"▶️ {video['title']}", expanded=False):
                col1, col2 = st.columns([1, 3])

                with col1:
                    st.image(video['thumbnail'])
                    st.caption(f"📅 {video['published_at'][:10]}")
                    st.caption(f"🆔 {video['video_id']}")

                with col2:
                    st.write(video['description'])
                    st.link_button(
                        "🔗 Watch",
                        f"https://www.youtube.com/watch?v={video['video_id']}"
                    )

                    # Get transcript button
                    if st.button(f"📝 Get Transcript", key=f"trans_{video['video_id']}"):
                        with st.spinner("Fetching transcript..."):
                            result = transcript_processor.get_and_format(
                                video['video_id'],
                                video['title'],
                                languages=preferred_languages,
                                format_type='timestamped'
                            )
                            st.session_state.transcripts[video['video_id']] = result
                            st.rerun()

                    # Display transcript
                    if video['video_id'] in st.session_state.transcripts:
                        result = st.session_state.transcripts[video['video_id']]

                        if result['success']:
                            metadata = result['metadata']
                            st.success(
                                f"✅ {metadata['language_code']} - "
                                f"{'Auto' if metadata['is_generated'] else 'Manual'} "
                                f"({metadata['entry_count']} entries)"
                            )

                            display_format = st.radio(
                                "Display:",
                                ["Timestamped", "Plain text"],
                                key=f"format_{video['video_id']}",
                                horizontal=True
                            )

                            # Reformat if needed
                            if display_format == "Plain text":
                                transcript_text = transcript_processor.formatter.format_plain_text(
                                    result['json_data']['transcript']
                                )
                            else:
                                transcript_text = result['formatted_text']

                            st.text_area(
                                "Transcript:",
                                transcript_text,
                                height=300,
                                key=f"text_{video['video_id']}"
                            )

                            # Download buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    "💾 JSON",
                                    data=json.dumps(
                                        result['json_data'],
                                        ensure_ascii=False,
                                        indent=2
                                    ),
                                    file_name=f"{video['video_id']}_transcript.json",
                                    mime="application/json",
                                    key=f"json_{video['video_id']}",
                                    use_container_width=True
                                )

                            with col2:
                                st.download_button(
                                    "💾 TXT",
                                    data=transcript_text,
                                    file_name=f"{video['video_id']}_transcript.txt",
                                    mime="text/plain",
                                    key=f"txt_{video['video_id']}",
                                    use_container_width=True
                                )
                        else:
                            st.error(f"❌ {result['error']}")

else:
    # Welcome screen
    st.info("👈 Use the sidebar to select a channel")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🚀 Quick Start

        1. **Click** "⭐ Load Default: Pinaki Bhattacharya" in sidebar
        2. **Load videos** from the channel
        3. **Get transcripts** for any video
        4. **Download** in JSON or TXT format

        ### ✨ Features

        - 🇧🇩 **1000 Bangladeshi Channels** pre-loaded
        - 🔍 **Search any channel** worldwide
        - 🌍 **Multi-language** support (Bangla, English, Hindi)
        - 📝 **View & download** transcripts
        - ⚡ **Fast & easy** to use
        """)

    with col2:
        st.markdown("""
        ### 📺 Channel Selection Methods

        **1. Bangladeshi Channels**
        - Browse 1000+ top BD channels
        - Pinaki Bhattacharya is default
        - Filter and search easily

        **2. Search Any Channel**
        - Search YouTube globally
        - Find any channel by name
        - See thumbnails and descriptions

        **3. Channel URL**
        - Paste any YouTube channel URL
        - Supports @username format
        - Quick and direct access
        """)

    # Featured channels
    st.subheader("⭐ Featured Bangladeshi Channels")
    featured = [
        Config.DEFAULT_CHANNEL,
        "Jamuna TV",
        "Prothom Alo",
        "10 Minute School",
        "Coke Studio Bangla",
        "BBC News বাংলা"
    ]

    cols = st.columns(3)
    for idx, name in enumerate(featured):
        with cols[idx % 3]:
            if st.button(f"📺 {name}", use_container_width=True, key=f"featured_{idx}"):
                load_channel(name)

# Footer
st.divider()
st.caption(f"🇧🇩 Made for Bangladesh | v{os.path.basename(__file__)} | Powered by Streamlit")
