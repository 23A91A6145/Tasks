import streamlit as st
from services.history import ChatHistory

_history = ChatHistory()


def render_session_manager() -> None:
    st.markdown('<div class="sidebar-section-title">💬 Sessions</div>', unsafe_allow_html=True)

    sessions = _history.list_sessions()
    if not sessions:
        st.caption("No saved sessions yet.")
        return

    current_id = st.session_state.get("session_id", "current")

    for sess in sessions[:10]:
        sid = sess["id"]
        msg_count = sess["count"]
        updated = sess.get("updated", "")[:16] if sess.get("updated") else ""

        title = f"Chat {msg_count} messages"
        if sid == current_id:
            title += " (current)"

        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                title,
                key=f"session_{sid}",
                use_container_width=True,
                help=f"Updated: {updated}" if updated else None,
            ):
                if sid != current_id:
                    _load_session(sid)

        with col2:
            if st.button("✕", key=f"del_{sid}", help="Delete session"):
                _history.delete(sid)
                if sid == st.session_state.get("session_id"):
                    st.session_state.messages = []
                    st.session_state.session_id = "current"
                    st.toast("Session deleted!", icon="🗑")
                st.rerun()


def _load_session(session_id: str) -> None:
    messages = _history.load(session_id)
    if messages:
        st.session_state.messages = messages
        st.session_state.session_id = session_id
        st.toast(f"Loaded session ({len(messages)} messages)", icon="📂")
        st.rerun()


def save_current_session() -> None:
    sid = st.session_state.get("session_id", "current")
    msgs = st.session_state.messages
    if msgs:
        _history.save(sid, msgs)
