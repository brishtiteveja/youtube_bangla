"""
Video Detail Page - Watch video, get transcript, and chat with AI
"""

import streamlit as st
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from config import Config
from transcript_api import TranscriptProcessor
from gemini_chat import GeminiChatBot

# Page configuration
st.set_page_config(
    page_title="Video Detail - YouTube Transcript Collector",
    page_icon="📺",
    layout=Config.LAYOUT
)

# Initialize session state
if 'video_transcripts' not in st.session_state:
    st.session_state.video_transcripts = {}
if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}

# Initialize components
@st.cache_resource
def get_transcript_processor():
    return TranscriptProcessor()

transcript_processor = get_transcript_processor()

# Check if video is selected
if 'selected_video' not in st.session_state or not st.session_state.selected_video:
    st.warning("No video selected. Please go back to Explore page.")
    if st.button("← Back to Explore"):
        st.switch_page("pages/1_🔍_Explore.py")
    st.stop()

video = st.session_state.selected_video

# Back button
if st.button("← Back to Explore"):
    st.switch_page("pages/1_🔍_Explore.py")

st.divider()

# Video header
col1, col2 = st.columns([2, 1])

with col1:
    # Video title
    st.title(video['title'])

    # Channel info
    if 'channel_name' in video:
        st.markdown(f"**📺 {video['channel_name']}**")

    # Video metadata
    col_date, col_views, col_likes, col_comments = st.columns(4)

    with col_date:
        st.metric("Published", video.get('published_at', 'N/A')[:10])

    with col_views:
        views = video.get('view_count', 0)
        if views >= 1000000:
            views_str = f"{views/1000000:.1f}M"
        elif views >= 1000:
            views_str = f"{views/1000:.1f}K"
        else:
            views_str = str(views)
        st.metric("Views", views_str)

    with col_likes:
        likes = video.get('like_count', 0)
        if likes >= 1000:
            likes_str = f"{likes/1000:.1f}K"
        else:
            likes_str = str(likes)
        st.metric("Likes", likes_str)

    with col_comments:
        comments = video.get('comment_count', 0)
        if comments >= 1000:
            comments_str = f"{comments/1000:.1f}K"
        else:
            comments_str = str(comments)
        st.metric("Comments", comments_str)

with col2:
    # Category badge
    if 'category' in video:
        st.info(f"📂 Category: **{video['category']}**")

st.divider()

# Embedded video player
st.subheader("📺 Watch Video")
st.video(f"https://www.youtube.com/watch?v={video['video_id']}")

# Video description
if video.get('description'):
    with st.expander("📄 Video Description"):
        st.write(video['description'])

st.divider()

# Transcript section
st.subheader("📝 Transcript & AI Chat")

# Get transcript button
if video['video_id'] not in st.session_state.video_transcripts:
    if st.button("📝 Get Transcript", type="primary", use_container_width=False):
        with st.spinner("Fetching transcript..."):
            result = transcript_processor.get_and_format(
                video['video_id'],
                video['title'],
                languages=['bn', 'en', 'hi'],
                format_type='timestamped'
            )
            st.session_state.video_transcripts[video['video_id']] = result
            st.rerun()
else:
    result = st.session_state.video_transcripts[video['video_id']]

    if result['success']:
        metadata = result['metadata']

        # Transcript metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success(f"✅ Language: {metadata['language_code']}")
        with col2:
            st.info(f"📊 Type: {'Auto-generated' if metadata['is_generated'] else 'Manual'}")
        with col3:
            st.info(f"📝 Entries: {metadata['entry_count']}")

        # Transcript display
        with st.expander("📄 View Full Transcript", expanded=False):
            display_format = st.radio(
                "Format:",
                ["Timestamped", "Plain text"],
                key="transcript_format",
                horizontal=True
            )

            if display_format == "Plain text":
                transcript_text = transcript_processor.formatter.format_plain_text(
                    result['json_data']['transcript']
                )
            else:
                transcript_text = result['formatted_text']

            st.text_area(
                "Transcript:",
                transcript_text,
                height=400,
                key="transcript_display"
            )

            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "💾 Download JSON",
                    data=json.dumps(
                        result['json_data'],
                        ensure_ascii=False,
                        indent=2
                    ),
                    file_name=f"{video['video_id']}_transcript.json",
                    mime="application/json",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    "💾 Download TXT",
                    data=transcript_text,
                    file_name=f"{video['video_id']}_transcript.txt",
                    mime="text/plain",
                    use_container_width=True
                )

        st.divider()

        # AI Chat Section
        st.subheader("💬 Chat with AI about this video")

        # Initialize chat if needed
        if video['video_id'] not in st.session_state.chat_sessions:
            try:
                chatbot = GeminiChatBot()
                plain_text = transcript_processor.formatter.format_plain_text(
                    result['json_data']['transcript']
                )
                chatbot.start_chat(plain_text, video['title'], video['video_id'])
                st.session_state.chat_sessions[video['video_id']] = chatbot
                st.session_state.chat_history[video['video_id']] = []
            except Exception as e:
                st.error(f"Could not initialize chat: {str(e)}")

        # Quick action buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋 Summarize Video", key="summarize", use_container_width=True):
                with st.spinner("Generating summary..."):
                    chatbot = st.session_state.chat_sessions[video['video_id']]
                    response = chatbot.get_summary()
                    if response['success']:
                        st.session_state.chat_history[video['video_id']].append(
                            ("📋 Summarize this video", response['response'])
                        )
                        st.rerun()

        with col2:
            if st.button("🔑 Extract Key Points", key="key_points", use_container_width=True):
                with st.spinner("Extracting key points..."):
                    chatbot = st.session_state.chat_sessions[video['video_id']]
                    response = chatbot.get_key_points()
                    if response['success']:
                        st.session_state.chat_history[video['video_id']].append(
                            ("🔑 What are the key points?", response['response'])
                        )
                        st.rerun()

        with col3:
            if st.button("🗑️ Clear Chat History", key="clear_chat", use_container_width=True):
                st.session_state.chat_history[video['video_id']] = []
                chatbot = st.session_state.chat_sessions[video['video_id']]
                chatbot.clear_chat()
                plain_text = transcript_processor.formatter.format_plain_text(
                    result['json_data']['transcript']
                )
                chatbot.start_chat(plain_text, video['title'], video['video_id'])
                st.rerun()

        # Display chat history
        if video['video_id'] in st.session_state.chat_history:
            history = st.session_state.chat_history[video['video_id']]
            if history:
                st.markdown("### Chat History")
                for question, answer in history:
                    with st.chat_message("user"):
                        st.write(question)
                    with st.chat_message("assistant"):
                        st.write(answer)

        # Chat input
        user_question = st.chat_input(
            "Ask a question about the video...",
            key="chat_input"
        )

        if user_question:
            with st.spinner("Thinking..."):
                chatbot = st.session_state.chat_sessions[video['video_id']]
                response = chatbot.ask(user_question)

                if response['success']:
                    st.session_state.chat_history[video['video_id']].append(
                        (user_question, response['response'])
                    )
                    st.rerun()
                else:
                    st.error(f"Error: {response['error']}")

    else:
        st.error(f"❌ {result['error']}")
        st.info("This video may not have transcripts available, or they may be disabled by the creator.")

# Footer
st.divider()
st.caption("📺 Video Detail | Watch, read transcript, and chat with AI")