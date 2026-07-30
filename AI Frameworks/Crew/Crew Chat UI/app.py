import streamlit as st
from crew.crew import CrewAssistant
from crew.config import settings
from services.logger import logger
from services.history import ChatHistory
from services.validator import InputValidator
from services.model_service import ModelService
from ui.theme import apply_theme
from ui.chat import render_messages, add_message
from ui.components import (
    render_input,
    render_suggested_prompts,
    render_control_buttons,
    render_stop_button,
    render_status,
    render_token_summary,
    render_search_bar,
)
from ui.sidebar import render_sidebar
from ui.session_manager import save_current_session

st.set_page_config(
    page_title="Crew Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

_history = ChatHistory()
_model_service = ModelService()


def init_state() -> None:
    if "messages" not in st.session_state:
        available = _model_service.get_chat_models()
        using_fallback = len(available) == 0 and settings.provider == "ollama"

        st.session_state.messages = []
        st.session_state.model = settings.active_model
        st.session_state.temperature = settings.OPENAI_MODEL_TEMPERATURE
        st.session_state.theme = "light"
        st.session_state.processing = False
        st.session_state.stop_requested = False
        st.session_state.needs_retry = False
        st.session_state.pending_query = ""
        st.session_state.active_template = ""
        st.session_state.template_context = ""
        st.session_state.api_ready = settings.is_ready
        st.session_state.provider = settings.provider
        st.session_state.session_id = "current"
        st.session_state.max_tokens = settings.MAX_TOKENS
        st.session_state.using_fallback = using_fallback
        st.session_state.available_models = available
        st.session_state.search_query = ""
        st.session_state.show_token_count = False
        st.session_state.custom_system_prompt = ""
        logger.info(
            f"Session v5 initialized — {settings.provider}, "
            f"{settings.active_model}, fallback={using_fallback}"
        )


def _build_effective_query(query: str) -> str:
    parts = []
    custom_prompt = st.session_state.get("custom_system_prompt", "")
    if custom_prompt:
        parts.append(f"[System: {custom_prompt}]")
    template_ctx = st.session_state.get("template_context", "")
    if template_ctx:
        parts.append(f"[Context: {template_ctx}]")
    if parts:
        return "\n\n".join(parts + [query])
    return query


def process_query(query: str) -> None:
    st.session_state.processing = True
    st.session_state.stop_requested = False

    query = _build_effective_query(query)
    add_message("user", query)

    logger.info(f"Query: {query[:80]}...")

    if st.session_state.get("stop_requested"):
        _reset_processing_state()
        return

    try:
        assistant = CrewAssistant()

        with st.spinner("🤖 Crew is working..."):
            response = assistant.run(query)

        if st.session_state.get("stop_requested"):
            _reset_processing_state()
            st.info("Generation stopped.")
            return

        add_message("assistant", response)

        if assistant.metrics.used_fallback:
            logger.info("Used fallback responder")
            st.info("💡 Running in fallback mode — install Ollama for AI responses.", icon="ℹ️")
        else:
            logger.info(f"Generated in {assistant.metrics.duration:.2f}s")

        save_current_session()

    except TimeoutError:
        logger.error("Request timed out")
        add_message("assistant", "⏱ The request timed out. Try a simpler query.")

    except Exception as e:
        logger.exception(f"Query failed: {e}")
        add_message("assistant", f"I encountered an error: {e}")

    finally:
        _reset_processing_state()


def _reset_processing_state() -> None:
    st.session_state.processing = False
    st.session_state.needs_retry = False
    st.session_state.pending_query = ""


def handle_retry() -> None:
    messages = st.session_state.messages
    user_msgs = [m for m in messages if m["role"] == "user"]
    if user_msgs:
        last_query = user_msgs[-1]["content"]
        st.session_state.messages = messages[:-2]
        process_query(last_query)


def main() -> None:
    init_state()
    apply_theme(st.session_state.theme)

    if not st.session_state.api_ready:
        st.warning(
            "⚠️ No LLM provider detected.\n\n"
            "**Option 1 (free, local):** [Install Ollama](https://ollama.ai) and pull a model:\n"
            "```\ncurl -fsSL https://ollama.ai/install.sh | sh\nollama pull llama3.2\n```\n"
            "**Option 2:** Set `OPENAI_API_KEY` in `.env` and restart."
        )
        st.stop()

    render_sidebar()

    chat_col, _ = st.columns([3, 1])
    with chat_col:
        render_messages()
        render_token_summary()
        render_status()
        render_stop_button()

        prompt = render_input()

        if prompt:
            process_query(prompt)
            st.rerun()

        if st.session_state.needs_retry:
            handle_retry()
            st.rerun()

        if st.session_state.pending_query:
            process_query(st.session_state.pending_query)
            st.rerun()

        render_search_bar()
        render_suggested_prompts()
        render_control_buttons()


if __name__ == "__main__":
    main()
