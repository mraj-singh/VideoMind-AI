import streamlit as st

from ui.chat import render_chat
from utils.export import (
    generate_pdf,
    generate_txt,
    sanitize_filename,
)


def navigation():
    """
    Top navigation shown at all times.
    """

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "📝 AI Summary",
            use_container_width=True,
            type="primary"
            if st.session_state.current_page == "summary"
            else "secondary",
        ):
            st.session_state.current_page = "summary"
            st.rerun()

    with col2:
        if st.button(
            "📄 Transcript",
            use_container_width=True,
            type="primary"
            if st.session_state.current_page == "transcript"
            else "secondary",
        ):
            st.session_state.current_page = "transcript"
            st.rerun()

    with col3:
        if st.button(
            "💬 Chat",
            use_container_width=True,
            type="primary"
            if st.session_state.current_page == "chat"
            else "secondary",
        ):
            st.session_state.current_page = "chat"
            st.rerun()


def empty_summary():
    """
    Empty state for Summary page.
    """

    st.subheader("📝 AI Summary")

    with st.container(border=True):

        st.markdown(
            """
### No summary available

Analyze a **YouTube video** or **upload a media file**
to generate a professional AI summary.

✨ Your report will include:

- Executive Summary
- Main Topics
- Key Takeaways
- Important Insights
- Action Items (if any)
- Final Thoughts
"""
        )


def empty_transcript():
    """
    Empty state for Transcript page.
    """

    st.subheader("📄 Transcript")

    with st.container(border=True):

        st.markdown(
            """
### No transcript available

Process a video to generate a complete transcript.

The transcript can then be:

- Read
- Downloaded
- Used for AI Chat
"""
        )


def render_tabs():

    navigation()

    st.divider()

    page = st.session_state.current_page

    result = st.session_state.result

    
    # SUMMARY
    

    if page == "summary":

        if result is None:

            empty_summary()
            return

        st.subheader(f"🎬 {result['title']}")
        st.write("")

        with st.container(border=True):

            st.subheader("📝 AI Report")

            st.markdown(result["summary"])

        st.write("")

        filename = sanitize_filename(result["title"])

        col1, col2 = st.columns(2)

        with col1:

            st.download_button(
                "📄Export Summary (PDF)",
                data=generate_pdf(result),
                file_name=f"{filename}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with col2:

            st.download_button(
                "📝Export Summary (TXT)",
                data=generate_txt(result["summary"]),
                file_name=f"{filename}_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )

    
    # TRANSCRIPT
    

    elif page == "transcript":

        if result is None:

            empty_transcript()
            return

        st.subheader(f"🎬 {result['title']}")

        st.write("")

        with st.container(border=True):

            st.text_area(
                "Transcript",
                result["transcript"],
                height=600,
            )

        st.write("")

        filename = sanitize_filename(result["title"])

        st.download_button(
            "📄 Export Transcript (TXT)",
            data=generate_txt(result["transcript"]),
            file_name=f"{filename}_transcript.txt",
            mime="text/plain",
            use_container_width=True,
        )

    
    # CHAT
    

    elif page == "chat":

        render_chat()