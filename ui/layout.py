import streamlit as st

from ui.components.video_card import render_video_card
from ui.components.summary_card import render_summary_card
from ui.components.insights_card import render_insights_card
from ui.components.transcript_panel import render_transcript_panel

from ui.chat import render_chat


def render_dashboard():
    """
    Render the complete VideoMind AI dashboard.
    """

    result = st.session_state.result

    # Welcome screen
    if result is None:

        st.info(
            "👋 Welcome to VideoMind AI\n\n"
            "Paste a YouTube URL or upload a video/audio file from the left sidebar "
            "and click **Process**."
        )

        return

    
    # Row 1
    

    left, right = st.columns(
        [1, 2],
        gap="large",
    )

    with left:
        render_video_card(result)

    with right:
        render_summary_card(result)

    st.divider()

    
    # Row 2
    

    left, right = st.columns(
        [1, 2],
        gap="large",
    )

    with left:
        render_insights_card(result)

    with right:
        render_transcript_panel(result)

    st.divider()

    
    # Chat
    

    render_chat()