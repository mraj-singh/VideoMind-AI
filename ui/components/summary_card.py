import streamlit as st


def render_summary_card(result):

    st.subheader("📝 Summary")

    if not result:

        st.info(
            "Summary will appear here."
        )

        return

    st.markdown(
        result["summary"]
    )