from datetime import datetime
from typing import List, Dict
import streamlit as st
from services.token_counter import TokenCounter

AVATARS = {"user": "🧑", "assistant": "🤖"}
TIMESTAMP_HELP = "Message sent at this time"


def render_welcome() -> None:
    st.markdown(
        f"""
        <div class="welcome-container">
            <div class="welcome-icon">🤖</div>
            <div class="welcome-title">How can I help you today?</div>
            <div class="welcome-subtitle">
                I'm a multi-agent AI assistant powered by CrewAI.
                Ask me anything — research, analysis, writing, and more.
            </div>
            <div class="welcome-features">
                <div class="welcome-feature">
                    <div class="welcome-feature-icon">🔍</div>
                    <div class="welcome-feature-label">Research</div>
                    <div class="welcome-feature-desc">Gather information</div>
                </div>
                <div class="welcome-feature">
                    <div class="welcome-feature-icon">📊</div>
                    <div class="welcome-feature-label">Analysis</div>
                    <div class="welcome-feature-desc">Extract insights</div>
                </div>
                <div class="welcome-feature">
                    <div class="welcome-feature-icon">✍️</div>
                    <div class="welcome-feature-label">Writing</div>
                    <div class="welcome-feature-desc">Draft content</div>
                </div>
                <div class="welcome-feature">
                    <div class="welcome-feature-icon">💡</div>
                    <div class="welcome-feature-label">Ideation</div>
                    <div class="welcome-feature-desc">Brainstorm ideas</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_messages() -> None:
    messages = st.session_state.messages
    if not messages:
        render_welcome()
        return

    search_query = st.session_state.get("search_query", "").strip().lower()
    show_token_count = st.session_state.get("show_token_count", False)

    for idx, msg in enumerate(messages):
        role = msg["role"]
        content = msg.get("content", "")
        ts = msg.get("timestamp", "")

        is_highlighted = False
        if search_query:
            is_highlighted = search_query in content.lower()

        highlight_class = " search-highlight" if is_highlighted else ""

        with st.chat_message(role, avatar=AVATARS.get(role, "🧑")):
            if is_highlighted and search_query:
                _render_highlighted_content(content, search_query)
            else:
                st.markdown(content)

            cols = st.columns([6, 1, 1])
            with cols[0]:
                st.markdown(
                    f'<div class="chat-footer"><span class="chat-timestamp">🕐 {ts}</span></div>',
                    unsafe_allow_html=True,
                )

            with cols[1]:
                if show_token_count:
                    tokens = TokenCounter.estimate(content)
                    st.markdown(
                        f'<span class="chat-token-badge">{tokens}</span>',
                        unsafe_allow_html=True,
                    )

            with cols[2]:
                if role == "assistant" and st.button("📋", key=f"copy_{idx}", help="Copy response"):
                    st.session_state.copy_content = content
                    st.toast("Copied!", icon="✅")


def _render_highlighted_content(content: str, query: str) -> None:
    import re
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    highlighted = pattern.sub(f'<mark class="search-match">{query}</mark>', content)
    st.markdown(highlighted, unsafe_allow_html=True)


def add_message(role: str, content: str) -> dict:
    msg = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "tokens": TokenCounter.estimate(content),
    }
    st.session_state.messages.append(msg)
    return msg
