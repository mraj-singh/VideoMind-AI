import streamlit as st

from core.pipeline import (
    run_pipeline,
    load_cached_pipeline,
)
from core.cache import (
    load_history,
    clear_all_cache,
)


def truncate(text: str, length: int = 38):
    """
    Shorten long titles for sidebar display.
    """

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


def render_sidebar():

    with st.sidebar:

        
        # Input
        

        st.subheader("🎥 Input Source")

        input_type = st.radio(
            "Choose Input",
            [
                "YouTube URL",
                "Upload File",
            ],
        )

        source = None

        # --------------------------        # Input Selection
        # --------------------------
        if input_type == "YouTube URL":

            if st.session_state.clear_youtube_url:
                st.session_state.youtube_url = ""
                st.session_state.clear_youtube_url = False

            source = st.text_input(
                "Paste YouTube URL",
                key="youtube_url",
            )

        else:

            uploaded_file = st.file_uploader(
                "Upload Audio / Video",
                type=[
                    "mp3",
                    "wav",
                    "mp4",
                    "m4a",
                    "mov",
                ],
            )

            if uploaded_file:

                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                source = uploaded_file.name

        
        # Analyze Button
        

        st.divider()

        if st.button(
            "Analyze Video",
            use_container_width=True,
        ):

            if not source:

                st.warning(
                    "Please provide an input."
                )

            else:

                from ui.progress import PipelineProgress

                progress = PipelineProgress()

                progress.update(
                    10,
                    "Preparing audio...",
                )

                result = run_pipeline(
                    source,
                    progress,
                )

                progress.complete()

                st.session_state.result = result
                st.session_state.cache_key = result["cache_key"]
                st.session_state.messages = []

                st.success(
                    "✅ Analysis completed!"
                )

                st.session_state.clear_youtube_url = True

                st.rerun()

        
        # History
        

        st.divider()

        st.subheader("📚 History")

        history = load_history()[:10]

        if not history:

            st.caption(
                "No videos analyzed yet.\n\n"
                "Your recent analyses will appear here."
            )

        else:

            for item in history:

                if st.button(
                    f"🎬 {truncate(item['title'])}",
                    key=f"open_{item['cache_key']}",
                    use_container_width=True,
                ):

                    with st.spinner(
                        "Loading analysis..."
                    ):

                        result = load_cached_pipeline(
                            item["cache_key"]
                        )

                    st.session_state.result = result
                    st.session_state.cache_key = result["cache_key"]
                    st.session_state.messages = result[
                        "messages"
                    ]

                    st.rerun()

        
        # Clear Cache
        

        if history:

            st.divider()

            if not st.session_state.get(
                "confirm_clear_cache",
                False,
            ):

                if st.button(
                    "⚠️ Clear Cache",
                    use_container_width=True,
                ):

                    st.session_state.confirm_clear_cache = True
                    st.rerun()

            else:

                st.warning(
                    """
⚠️ **Clear all cached data?**

This will permanently delete:

- Processed videos
- AI summaries
- Transcripts
- Chat history
- Vector databases

**This action cannot be undone.**
"""
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "Yes, Clear",
                        use_container_width=True,
                    ):

                        clear_all_cache()

                        st.session_state.result = None
                        st.session_state.cache_key = None
                        st.session_state.messages = []
                        st.session_state.confirm_clear_cache = False

                        st.toast(
                            "🧹 Cache cleared successfully!",
                            icon="✅",
                        )

                        st.rerun()

                with col2:

                    if st.button(
                        "Cancel",
                        use_container_width=True,
                    ):

                        st.session_state.confirm_clear_cache = False
                        st.rerun()