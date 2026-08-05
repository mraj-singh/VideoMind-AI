import streamlit as st


def render_transcript_panel(result):

    st.subheader("📄 Transcript")

    if not result:

        st.info(
            "Transcript will appear here."
        )

        return

    st.text_area(
        "",
        result["transcript"],
        height=350,
    )