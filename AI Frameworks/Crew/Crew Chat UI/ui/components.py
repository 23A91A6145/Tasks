import streamlit as st
from services.history import ChatHistory
from services.validator import InputValidator
from services.token_counter import TokenCounter
from services.logger import logger

SUGGESTED_PROMPTS = [
    "What is CrewAI and how does it work?",
    "Explain how AI agents collaborate",
    "Write a Python function to sort a list",
    "Compare REST and GraphQL APIs",
    "Explain the CAP theorem",
]

PROMPT_TEMPLATES = {
    "General Q&A": "Answer the following question thoroughly and clearly.",
    "Code Review": "Review the following code for bugs, style issues, and improvements.",
    "Summarize": "Provide a concise summary of the following text.",
    "Brainstorm": "Brainstorm creative ideas and solutions for the following topic.",
    "Explain Simply": "Explain the following concept in simple terms for a beginner.",
    "Translate": "Translate the following text accurately while preserving tone.",
    "Debug": "Help debug the following code and explain the fix.",
    "Write Code": "Write clean, well-documented code for the following specification.",
}

_history = ChatHistory()


def render_input() -> str | None:
    disabled = (
        st.session_state.get("processing", False)
        or not st.session_state.get("api_ready", False)
    )
    placeholder = "Type your message here... Ctrl+Enter to send"
    if not st.session_state.get("api_ready", False):
        placeholder = "No LLM provider configured..."
    elif st.session_state.get("processing", False):
        placeholder = "Waiting for response..."

    prompt = st.chat_input(placeholder, disabled=disabled, key="chat_input")

    if prompt:
        valid, error = InputValidator.validate_query(prompt)
        if not valid:
            logger.warning(f"Validation failed: {error}")
            st.error(f"⚠️ {error}")
            return None
        sanitized = InputValidator.sanitize(prompt)
        return sanitized
    return None


def render_suggested_prompts() -> None:
    if st.session_state.messages:
        return

    st.markdown('<div class="suggested-area">', unsafe_allow_html=True)
    st.markdown("#### Try asking:")
    rows = [SUGGESTED_PROMPTS[i:i+3] for i in range(0, len(SUGGESTED_PROMPTS), 3)]
    for row in rows:
        cols = st.columns(len(row))
        for i, prompt in enumerate(row):
            key = f"suggest_{hash(prompt) % (10**8)}"
            if cols[i].button(prompt, use_container_width=True, key=key):
                st.session_state.pending_query = prompt
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_control_buttons() -> None:
    if not st.session_state.messages:
        return

    st.markdown('<div class="controls-bar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 4])

    with col1:
        if st.button("🗑 Clear", use_container_width=True, key="clear_btn"):
            st.session_state.messages = []
            st.rerun()

    with col2:
        if st.button("🔄 Retry", use_container_width=True, key="retry_btn"):
            st.session_state.needs_retry = True
            st.rerun()

    with col3:
        export_md = _history.export_markdown(st.session_state.messages)
        st.download_button(
            "📥 MD",
            data=export_md,
            file_name="chat_export.md",
            mime="text/markdown",
            use_container_width=True,
            key="export_md_btn",
        )

    with col4:
        export_json = _history.export_json(st.session_state.messages)
        st.download_button(
            "📥 JSON",
            data=export_json,
            file_name="chat_export.json",
            mime="application/json",
            use_container_width=True,
            key="export_json_btn",
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_token_summary() -> None:
    if not st.session_state.messages:
        return
    summary = TokenCounter.summarize_token_usage(st.session_state.messages)
    st.markdown(
        f'<div class="token-summary">📊 {summary}</div>',
        unsafe_allow_html=True,
    )


def render_search_bar() -> None:
    if not st.session_state.messages:
        return

    with st.expander("🔍 Search messages", expanded=False):
        search = st.text_input(
            "Search",
            value=st.session_state.get("search_query", ""),
            key="search_input",
            placeholder="Type to search...",
            label_visibility="collapsed",
        )
        if search != st.session_state.get("search_query", ""):
            st.session_state.search_query = search
            st.rerun()

        if st.session_state.get("search_query"):
            if st.button("Clear search", use_container_width=True):
                st.session_state.search_query = ""
                st.rerun()


def render_stop_button() -> None:
    if st.session_state.get("processing", False):
        st.markdown('<div class="stop-btn">', unsafe_allow_html=True)
        if st.button("⏹ Stop Generation", use_container_width=True, type="secondary"):
            st.session_state.stop_requested = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_status() -> None:
    if st.session_state.get("processing"):
        st.markdown(
            f"""
            <div class="status-processing">
                <div class="status-dot"></div>
                <span class="status-label">🤖 Crew is working...</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
