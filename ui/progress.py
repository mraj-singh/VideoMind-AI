import streamlit as st


class PipelineProgress:

    def __init__(self):

        self.progress = st.progress(0)

        self.status = st.empty()

    def update(
        self,
        percent: int,
        message: str,
    ):

        self.progress.progress(percent)

        self.status.markdown(
            f"**{message}**"
        )

    def complete(self):

        self.progress.progress(100)

        self.status.success(
            "Processing Complete!"
        )