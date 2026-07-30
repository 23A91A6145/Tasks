import streamlit as st
from crew.config import settings
from services.history import ChatHistory
from services.token_counter import TokenCounter
from services.model_service import ModelService
from services.provider_service import get_providers, get_available_providers
from ui.session_manager import render_session_manager

_model_service = ModelService()


def render_sidebar() -> None:
    with st.sidebar:
        _render_header()
        _render_provider_status()

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_config_section()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_provider_selector()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_system_prompt_editor()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_templates_section()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        render_session_manager()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_statistics_section()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_agent_section()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_theme_section()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
        _render_shortcuts_section()
        st.markdown("</div>", unsafe_allow_html=True)

        _render_clear_button()


def _render_header() -> None:
    provider = st.session_state.get("provider", settings.provider)
    model = st.session_state.get("model", settings.active_model)
    fallback = st.session_state.get("using_fallback", False)

    status_dot = "🟡" if fallback else ("🟢" if provider != "none" else "🔴")
    status_label = "Fallback" if fallback else (provider.title() if provider != "none" else "Offline")

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
            <span style="font-size:1.75rem;">🤖</span>
            <div>
                <div style="font-weight:700;font-size:1rem;">Crew Assistant</div>
                <div style="font-size:0.7rem;color:#64748b;">
                    {status_dot} {status_label} · <code>{model}</code>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_provider_status() -> None:
    available_models = _model_service.get_chat_models()
    if available_models:
        st.markdown(
            f'<div style="font-size:0.7rem;color:#64748b;margin-bottom:0.5rem;">'
            f'📦 {len(available_models)} model(s): {", ".join(available_models[:3])}'
            f'{"..." if len(available_models) > 3 else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_provider_selector() -> None:
    st.markdown('<div class="sidebar-section-title">🔌 Provider</div>', unsafe_allow_html=True)
    providers = get_available_providers()
    current = st.session_state.get("provider", settings.provider)

    options = []
    for p in providers:
        label = p["display"]
        if p["configured"]:
            label += " ✅"
        options.append(label)

    names = [p["name"] for p in providers]
    idx = names.index(current) if current in names else 0

    selected = st.selectbox(
        "Provider",
        options,
        index=idx,
        key="provider_selector",
        label_visibility="collapsed",
    )

    selected_name = names[options.index(selected)]
    if selected_name != current:
        st.session_state.provider = selected_name
        st.toast(f"Switched to {selected_name}", icon="🔄")
        st.rerun()


def _render_system_prompt_editor() -> None:
    st.markdown('<div class="sidebar-section-title">📝 System Prompt</div>', unsafe_allow_html=True)
    current = st.session_state.get("custom_system_prompt", "")
    new_prompt = st.text_area(
        "Custom instructions for agents",
        value=current,
        placeholder="Leave empty for defaults. Custom instructions override agent backstories.",
        height=80,
        key="system_prompt_editor",
        label_visibility="collapsed",
    )
    if new_prompt != current:
        st.session_state.custom_system_prompt = new_prompt
        if new_prompt:
            st.toast("System prompt updated", icon="✅")
        else:
            st.toast("Default prompts restored", icon="↩️")


def _render_config_section() -> None:
    st.markdown('<div class="sidebar-section-title">⚙ Model</div>', unsafe_allow_html=True)

    provider = st.session_state.get("provider", settings.provider)
    if provider == "ollama":
        available = _model_service.get_chat_models()
        current = settings.OLLAMA_MODEL_NAME
        if available:
            selected = st.selectbox(
                "Model",
                available,
                index=available.index(current) if current in available else 0,
                key="sidebar_ollama_model",
                label_visibility="collapsed",
            )
            if selected != current:
                st.session_state.model = selected
                st.toast(f"Model set to {selected}", icon="✅")
                st.rerun()
        else:
            st.markdown(f"**Model:** `{current}`")
    else:
        models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        selected = st.selectbox(
            "Model",
            models,
            index=models.index(st.session_state.model)
            if st.session_state.model in models
            else 0,
            key="sidebar_model",
            label_visibility="collapsed",
        )
        if selected != st.session_state.model:
            st.session_state.model = selected

    temp = st.slider(
        "Temperature",
        min_value=0.0, max_value=2.0,
        value=st.session_state.temperature,
        step=0.1, key="sidebar_temp",
    )
    if temp != st.session_state.temperature:
        st.session_state.temperature = temp

    max_tokens = st.number_input(
        "Max tokens",
        min_value=256, max_value=8192,
        value=st.session_state.get("max_tokens", 2048),
        step=256, key="sidebar_max_tokens",
    )
    if max_tokens != st.session_state.get("max_tokens"):
        st.session_state.max_tokens = max_tokens

    show_tokens = st.checkbox(
        "Show token counts",
        value=st.session_state.get("show_token_count", False),
        key="sidebar_show_tokens",
    )
    if show_tokens != st.session_state.get("show_token_count"):
        st.session_state.show_token_count = show_tokens
        st.rerun()


def _render_templates_section() -> None:
    st.markdown('<div class="sidebar-section-title">📋 Templates</div>', unsafe_allow_html=True)
    templates = {
        "General Q&A": "Answer the following question thoroughly and clearly.",
        "Code Review": "Review the following code for bugs, style issues, and improvements.",
        "Summarize": "Provide a concise summary of the following text.",
        "Brainstorm": "Brainstorm creative ideas and solutions for the following topic.",
        "Explain Simply": "Explain the following concept in simple terms for a beginner.",
        "Translate": "Translate the following text accurately while preserving tone.",
        "Debug": "Help debug the following code and explain the fix.",
        "Write Code": "Write clean, well-documented code for the following specification.",
    }
    selected = st.selectbox(
        "Template", ["None"] + list(templates.keys()),
        key="template_selector", label_visibility="collapsed",
    )
    if selected != "None" and selected != st.session_state.get("active_template"):
        st.session_state.active_template = selected
        st.session_state.template_context = templates[selected]
        st.toast(f"Template '{selected}' applied!", icon="📋")
        st.rerun()
    if st.session_state.get("active_template"):
        st.caption(f"Active: **{st.session_state.active_template}**")
        if st.button("Clear", use_container_width=True, key="clear_template"):
            st.session_state.active_template = ""
            st.session_state.template_context = ""
            st.rerun()


def _render_statistics_section() -> None:
    st.markdown('<div class="sidebar-section-title">📊 Stats</div>', unsafe_allow_html=True)
    messages = st.session_state.messages
    if not messages:
        st.caption("No messages yet.")
        return

    stats = ChatHistory.compute_stats(messages)
    token_stats = TokenCounter.estimate_messages(messages)
    st.markdown(
        f"""
        <div class="stat-row"><span class="stat-label">Messages</span><span class="stat-value">{stats['total']}</span></div>
        <div class="stat-row"><span class="stat-label">You</span><span class="stat-value">{stats['user']}</span></div>
        <div class="stat-row"><span class="stat-label">AI</span><span class="stat-value">{stats['assistant']}</span></div>
        <div class="stat-row"><span class="stat-label">Tokens</span><span class="stat-value">{token_stats['total']:,}</span></div>
        <div class="stat-row"><span class="stat-label">Cost</span><span class="stat-value">Free</span></div>
        """,
        unsafe_allow_html=True,
    )


def _render_agent_section() -> None:
    st.markdown('<div class="sidebar-section-title">🤖 Agents</div>', unsafe_allow_html=True)
    agents_info = [
        ("🔍 Research Specialist", "Gathers relevant information"),
        ("📊 Analysis Expert", "Extracts insights and patterns"),
        ("✍️ Response Writer", "Synthesizes final response"),
    ]
    for role, desc in agents_info:
        st.markdown(
            f"""
            <div class="sidebar-agent">
                <div class="sidebar-agent-role">{role}</div>
                <div class="sidebar-agent-goal">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_theme_section() -> None:
    st.markdown('<div class="sidebar-section-title">🎨 Theme</div>', unsafe_allow_html=True)
    current = st.session_state.theme
    selected = st.radio(
        "Theme", ["light", "dark"],
        index=0 if current == "light" else 1,
        key="sidebar_theme", horizontal=True, label_visibility="collapsed",
    )
    if selected != current:
        st.session_state.theme = selected
        st.rerun()


def _render_shortcuts_section() -> None:
    st.markdown('<div class="sidebar-section-title">⌨ Shortcuts</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:0.7rem;color:#64748b;">
            <code>Ctrl+Enter</code> Send message<br>
            <code>Escape</code> Clear input<br>
            <code>Ctrl+K</code> Focus search
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_clear_button() -> None:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear Conversation", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.rerun()
