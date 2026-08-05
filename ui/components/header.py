import streamlit as st


def render_header():
    """
    Render the application header.
    """

    st.title("🎬 VideoMind AI")

    st.caption(
        "Understand any YouTube video, meeting, lecture or podcast using AI."
    )

    st.divider()