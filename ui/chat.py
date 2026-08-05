import streamlit as st

from core.rag_engine import ask_question
from core.cache import save_chat
from utils.export import (
    generate_chat_txt,
    sanitize_filename,
)


def render_chat_messages():
    """
    Display chat history.
    """

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])


def process_chat(prompt: str):
    """
    Process a user message and generate an AI response.
    """

    # Save user message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    save_chat(
        st.session_state.cache_key,
        st.session_state.messages,
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # Generate AI response

    with st.chat_message("assistant"):

        with st.spinner(
            "🧠 Searching transcript..."
        ):

            answer = ask_question(
                st.session_state.cache_key,
                prompt,
            )

        st.markdown(answer)

    # Save assistant response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    save_chat(
        st.session_state.cache_key,
        st.session_state.messages,
    )


def render_chat():
    """
    Render complete chat interface.
    """

    # No analysis yet

    if not st.session_state.get("cache_key"):

        st.subheader("💬 AI Chat")

        with st.container(border=True):

            st.markdown(
                """
### No video available

Analyze a video first to start chatting with your content.

You can ask questions about:

- 📌 Key concepts
- 📝 Summary
- 🎯 Important topics
- 💡 Insights
- ❓ Specific details
"""
            )

        return

    # Header

    st.subheader(
        f"💬 Chat • {st.session_state.result['title']}"
    )

    st.caption(
        "Ask questions about the processed video."
    )

    st.write("")

    # Empty chat state

    if not st.session_state.messages:

        with st.container(border=True):

            st.markdown(
                """
### 👋 Start a conversation

Try asking questions like:

- Summarize this video.
- What are the key takeaways?
- Explain the main topic.
- List the important insights.
- What action items were discussed?
"""
            )

    # Existing conversation

    render_chat_messages()

    # Chat Input

    prompt = st.chat_input(
        "Ask anything about the transcript..."
    )

    if prompt:

        process_chat(prompt)

        st.rerun()

    # Export Chat

    if st.session_state.messages:

        st.write("")

        filename = sanitize_filename(
            st.session_state.result["title"]
        )

        st.download_button(
            "💬 Export Chat (TXT)",
            data=generate_chat_txt(
                st.session_state.messages
            ),
            file_name=f"{filename}_chat.txt",
            mime="text/plain",
            use_container_width=True,
        )