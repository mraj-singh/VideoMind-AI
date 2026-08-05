from dotenv import load_dotenv

load_dotenv()

import streamlit as st

from ui.sidebar import render_sidebar
from ui.tabs import render_tabs

# Page Configuration

st.set_page_config(
    page_title="VideoMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Session State Initialization

if "clear_youtube_url" not in st.session_state:
    st.session_state.clear_youtube_url = False

if "result" not in st.session_state:
    st.session_state.result = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "summary"

if "cache_key" not in st.session_state:
    st.session_state.cache_key = None

if "confirm_clear_cache" not in st.session_state:
    st.session_state.confirm_clear_cache = False

# Header

st.title("🎬 VideoMind AI")

st.markdown(
    """
 **Intelligent Video Analysis & RAG Assistant**
"""
)

with st.expander(
    "✨ What can VideoMind AI do?",
    expanded=False,
):

    st.markdown(
        """
- 🎥 Analyze YouTube videos
- 📂 Upload audio or video files
- 🎙 Generate accurate transcripts with Faster Whisper
- 📝 Create AI-powered summaries
- 💬 Chat with your content using Retrieval-Augmented Generation (RAG)
- 📄 Export summaries, transcripts and chat history
"""
    )

st.divider()

# Sidebar

render_sidebar()

# Main Content

render_tabs()