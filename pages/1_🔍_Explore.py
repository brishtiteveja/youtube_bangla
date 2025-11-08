"""
Explore Page - Browse videos by category
Carousel view of top videos across categories
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from config import Config
from youtube_api import YouTubeAPIClient
from channel_database import ChannelDatabase

# Page configuration
st.set_page_config(
    page_title="Explore - YouTube Transcript Collector",
    page_icon="🔍",
    layout=Config.LAYOUT
)

# Initialize session state
if 'explore_videos' not in st.session_state:
    st.session_state.explore_videos = {}  # {category: [videos]}

# Initialize components
@st.cache_resource
def get_api_client():
    return YouTubeAPIClient(Config.YOUTUBE_API_KEY)

@st.cache_data
def get_channel_database():
    return ChannelDatabase()

api_client = get_api_client()
db = get_channel_database()


def load_category_videos(category: str, num_videos: int = 5):
    """Load videos for a category"""
    if category in st.session_state.explore_videos:
        return st.session_state.explore_videos[category]

    # Get top channels from this category
    category_channels = db.get_channels_by_category(category, limit=3)

    videos = []
    for channel in category_channels:
        try:
            # Try to get channel_id
            channel_id = channel.get('channel_id')
            if not channel_id:
                # Search by name
                search_results = api_client.search_channels(channel['name'], max_results=1)
                if search_results:
                    channel_id = search_results[0]['channel_id']

            if channel_id:
                # Get channel info
                channel_info = api_client.get_channel_info(channel_id)
                if channel_info:
                    # Get latest videos
                    channel_videos = api_client.get_channel_videos(
                        channel_info['channel_id'],
                        max_results=2,
                        show_progress=False
                    )

                    # Enrich with stats
                    enriched = api_client.enrich_videos_with_stats(channel_videos)

                    # Add channel info
                    for video in enriched:
                        video['channel_name'] = channel_info['title']
                        video['channel_thumbnail'] = channel_info['thumbnail']
                        video['category'] = category

                    videos.extend(enriched)

                    if len(videos) >= num_videos:
                        break
        except Exception as e:
            continue

    # Store in cache
    st.session_state.explore_videos[category] = videos[:num_videos]
    return videos[:num_videos]


# Back to Home button
col_back, col_spacer = st.columns([1, 5])
with col_back:
    if st.button("← Home", key="back_to_home", use_container_width=True):
        # Clear any query params and navigate to main page
        st.query_params.clear()
        st.rerun()

st.divider()

# Title
st.title("🔍 Explore Videos")
st.markdown("Discover trending videos from top Bangladeshi channels across all categories")

# Get top 10 categories with most channels
all_categories = db.get_all_categories()
category_stats = db.get_category_stats()

# Sort by channel count and get top 10
top_categories = sorted(
    [(cat, count) for cat, count in category_stats.items() if cat != 'General' and count > 0],
    key=lambda x: x[1],
    reverse=True
)[:10]

# Load videos for all top categories
with st.spinner("Loading videos from top categories..."):
    for category, count in top_categories:
        if category not in st.session_state.explore_videos:
            load_category_videos(category, num_videos=5)

# Display category carousels
for category, count in top_categories:
    st.divider()

    # Category header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.header(f"📂 {category}")
        st.caption(f"{count} channels | Latest videos")
    with col2:
        st.write("")
        if st.button(f"View All →", key=f"view_all_{category}", use_container_width=True):
            st.info(f"Coming soon: Full {category} page")

    # Get videos for this category
    videos = st.session_state.explore_videos.get(category, [])

    if videos:
        # Display videos in horizontal carousel (5 columns)
        cols = st.columns(5)

        for idx, video in enumerate(videos[:5]):
            with cols[idx]:
                # Video thumbnail
                st.image(video['thumbnail'], use_column_width=True)

                # Video title (truncated)
                title = video['title']
                if len(title) > 50:
                    title = title[:50] + "..."
                st.markdown(f"**{title}**")

                # Channel name
                if 'channel_name' in video:
                    st.caption(f"📺 {video['channel_name'][:25]}")

                # Stats
                if 'view_count' in video:
                    views = video['view_count']
                    if views >= 1000000:
                        views_str = f"{views/1000000:.1f}M"
                    elif views >= 1000:
                        views_str = f"{views/1000:.1f}K"
                    else:
                        views_str = str(views)
                    st.caption(f"👁️ {views_str} views")

                # Watch button - navigates to video detail page
                if st.button("▶️ Watch", key=f"watch_{video['video_id']}", use_container_width=True):
                    # Store video data in session state
                    st.session_state.selected_video = video
                    # Use query params to navigate
                    st.query_params["page"] = "video_detail"
                    st.query_params["video_id"] = video['video_id']
                    st.rerun()
    else:
        st.info(f"No videos available for {category}")

# Footer
st.divider()
st.caption("🔍 Explore | Discover videos across all categories")