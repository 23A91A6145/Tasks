import csv
import json
import logging
import sys
import time
import uuid
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from config.settings import LLM_PROVIDER, LLM_MODEL
from crews.support_crew import SupportCrew
from api.history_store import HistoryStore

logger = logging.getLogger(__name__)

store = HistoryStore()

st.set_page_config(
    page_title="Support Triage Crew",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .agent-badge {
        display: inline-block; padding: 2px 12px; border-radius: 4px;
        font-size: 0.8rem; font-weight: 600; margin-right: 6px;
    }
    .badge-billing { background: #0a2e2e; color: #00d4d4; border: 1px solid #00d4d4; }
    .badge-technical { background: #1a0a2e; color: #a855f7; border: 1px solid #a855f7; }
    .badge-sales { background: #0a2e0a; color: #22c55e; border: 1px solid #22c55e; }
    .badge-escalate { background: #2e1a0a; color: #f97316; border: 1px solid #f97316; }
    .tool-badge {
        display: inline-block; padding: 1px 10px; border-radius: 10px;
        font-size: 0.75rem; background: #333; color: #bbb; margin-right: 4px;
    }
    .val-passed { color: #22c55e; font-weight: 600; }
    .val-reviewed { color: #f97316; font-weight: 600; }
    .welcome-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 12px; padding: 2rem; text-align: center;
        border: 1px solid #333;
    }
    .exec-time { color: #666; font-size: 0.75rem; }
</style>
""", unsafe_allow_html=True)

COLORS = {
    "billing": {"class": "badge-billing", "icon": "💳", "label": "BILLING"},
    "technical": {"class": "badge-technical", "icon": "🔧", "label": "TECHNICAL"},
    "sales": {"class": "badge-sales", "icon": "📊", "label": "SALES"},
    "escalate": {"class": "badge-escalate", "icon": "⚠️", "label": "ESCALATED"},
}


def agent_badge_html(classification: str) -> str:
    info = COLORS.get(classification, COLORS["escalate"])
    return f'<span class="agent-badge {info["class"]}">{info["icon"]} {info["label"]}</span>'


def tool_badges_html(tools: list) -> str:
    return "".join(f'<span class="tool-badge">{t}</span>' for t in tools)


def init_state():
    defaults = {
        "messages": [],
        "processing": False,
        "conversation_id": None,
        "feedback_sent": set(),
        "export_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def run_query(query: str) -> dict:
    st.session_state.processing = True
    try:
        history_for_context = []
        if st.session_state.conversation_id:
            entries = store.get_conversation(st.session_state.conversation_id)
            history_for_context = [
                {"role": "user", "content": e["query"]}
                for e in reversed(entries[-6:])
            ]

        start = time.time()
        crew = SupportCrew(query, conversation_history=history_for_context)
        result = crew.run()
        elapsed = round(time.time() - start, 2)

        if not st.session_state.conversation_id:
            st.session_state.conversation_id = f"conv_{uuid.uuid4().hex[:12]}"

        entry_id = store.add_entry(
            query=result["query"],
            classification=result["classification"],
            tools_used=result.get("tools_used", []),
            routing_rationale=result.get("routing_rationale", ""),
            response=result["response"],
            validated=result.get("validated", False),
            validation_report=result.get("validation_report", ""),
            execution_time=elapsed,
            conversation_id=st.session_state.conversation_id,
        )
        result["id"] = entry_id
        result["execution_time"] = elapsed
        return result
    finally:
        st.session_state.processing = False


def render_message(msg: dict):
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            r = msg["content"]
            if isinstance(r, dict):
                classification = r.get("classification", "unknown")
                tools = r.get("tools_used", [])
                validated = r.get("validated", False)
                val_report = r.get("validation_report", "")
                elapsed = r.get("execution_time", 0)
                entry_id = r.get("id")

                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(agent_badge_html(classification), unsafe_allow_html=True)
                with col2:
                    if tools:
                        st.markdown(tool_badges_html(tools), unsafe_allow_html=True)
                    if validated:
                        st.markdown('<span class="val-passed">✓ Validated</span>', unsafe_allow_html=True)
                    elif classification != "escalate":
                        st.markdown('<span class="val-reviewed">⚠ Reviewed</span>', unsafe_allow_html=True)

                if val_report and "APPROVED" not in val_report:
                    with st.expander("Validation Report"):
                        st.caption(val_report)

                if elapsed:
                    st.markdown(f'<span class="exec-time">{elapsed:.1f}s</span>', unsafe_allow_html=True)

                st.divider()
                st.markdown(r.get("response", ""))

                if entry_id and entry_id not in st.session_state.feedback_sent:
                    fb_col1, fb_col2, _ = st.columns([1, 1, 10])
                    with fb_col1:
                        if st.button("👍", key=f"up_{entry_id}", help="Helpful"):
                            store.update_feedback(entry_id, 1)
                            st.session_state.feedback_sent.add(entry_id)
                            st.rerun()
                    with fb_col2:
                        if st.button("👎", key=f"down_{entry_id}", help="Not helpful"):
                            store.update_feedback(entry_id, -1)
                            st.session_state.feedback_sent.add(entry_id)
                            st.rerun()


def render_chat():
    for msg in st.session_state.messages:
        render_message(msg)

    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card">
            <h2>🎧 Support Triage Crew</h2>
            <p style="color: #888;">Multi-agent AI customer support system</p>
            <p style="color: #666; font-size: 0.9rem; margin-top: 1rem;">
                Ask a support question and get routed to the right specialist —
                Billing, Technical, or Sales. Responses are validated for quality.
            </p>
            <div style="margin-top: 1.5rem; display: flex; gap: 0.5rem; justify-content: center; flex-wrap: wrap;">
                <span class="agent-badge badge-billing">💳 Billing</span>
                <span class="agent-badge badge-technical">🔧 Technical</span>
                <span class="agent-badge badge-sales">📊 Sales</span>
                <span class="agent-badge badge-escalate">⚠️ Escalate</span>
            </div>
            <div style="margin-top: 1rem; color: #555; font-size: 0.85rem;">
                Try: "I was charged twice" · "Can't log in" · "Compare plans"
            </div>
        </div>
        """, unsafe_allow_html=True)

    prompt = st.chat_input(
        "Describe your support issue...",
        disabled=st.session_state.processing,
        key="chat_input",
    )
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.status("Processing...", expanded=True) as status:
                st.markdown("🔄 Routing to specialist...")
                try:
                    result = run_query(prompt)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                    status.update(label="Complete", state="complete", expanded=False)
                except Exception as e:
                    status.update(label="Error", state="error")
                    st.error("An error occurred while processing your request.")
                    logger.error("Chat error: %s", e)
            render_message(st.session_state.messages[-1])

        st.rerun()


def prepare_csv_download():
    search_term = st.session_state.get("history_search", "")
    cat_filter = st.session_state.get("history_cat", "All")
    classification = cat_filter if cat_filter != "All" else ""
    entries = store.get_all(limit=500, classification=classification, search=search_term)
    output = StringIO()
    w = csv.writer(output)
    w.writerow(["id", "timestamp", "query", "classification", "tools_used",
                 "response", "validated", "execution_time", "feedback"])
    for e in entries:
        w.writerow([
            e["id"], e["timestamp"], e["query"], e["classification"],
            json.dumps(e["tools_used"]), e["response"], e["validated"],
            e["execution_time"], e.get("feedback", ""),
        ])
    output.seek(0)
    st.session_state.export_data = output.getvalue()


def render_history():
    st.header("History")

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Search queries...",
                                     label_visibility="collapsed", key="history_search")
    with col2:
        cat_filter = st.selectbox("Category", ["All", "billing", "technical", "sales", "escalate"],
                                   label_visibility="collapsed", key="history_cat")
    with col3:
        limit = st.selectbox("Show", [20, 50, 100], index=1, label_visibility="collapsed", key="history_limit")
    with col4:
        st.button("📥 Prepare CSV", use_container_width=True, on_click=prepare_csv_download)

    if st.session_state.export_data:
        st.download_button("Download CSV", st.session_state.export_data,
                           "history.csv", "text/csv", key="download_csv")

    entries = store.get_all(
        limit=limit,
        classification=cat_filter if cat_filter != "All" else "",
        search=search_term,
    )

    if not entries:
        st.info("No conversation history yet.")
        return

    for entry in entries:
        classification = entry["classification"]
        validated = entry.get("validated", False)
        tools = entry.get("tools_used", [])
        feedback = entry.get("feedback")

        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 1.2, 1, 0.8, 0.5])
            with c1:
                short_q = entry["query"][:80] + ("..." if len(entry["query"]) > 80 else "")
                st.markdown(f"**{short_q}**")
            with c2:
                st.markdown(agent_badge_html(classification), unsafe_allow_html=True)
            with c3:
                st.markdown(tool_badges_html(tools), unsafe_allow_html=True) if tools else st.markdown("—")
            with c4:
                if validated:
                    st.markdown('<span class="val-passed">✓</span>', unsafe_allow_html=True)
                elif classification == "escalate":
                    st.markdown("—")
                else:
                    st.markdown('<span class="val-reviewed">⚠</span>', unsafe_allow_html=True)
            with c5:
                if feedback == 1:
                    st.markdown("👍")
                elif feedback == -1:
                    st.markdown("👎")

            with st.expander("View response"):
                st.caption(f"{entry['timestamp']}  |  {entry['execution_time']}s  |  ID: {entry['id']}")
                st.markdown(entry["response"])
                if entry.get("validation_report") and "APPROVED" not in entry.get("validation_report", ""):
                    st.markdown(f"**Validation:** {entry['validation_report'][:200]}")
                if entry.get("conversation_id"):
                    st.caption(f"Conversation: `{entry['conversation_id'][:20]}...`")

            st.divider()


def render_settings():
    st.header("Settings")
    with st.container():
        st.markdown("### LLM Configuration")
        st.json({"Provider": LLM_PROVIDER, "Model": LLM_MODEL})

    st.divider()

    with st.container():
        st.markdown("### System Statistics")
        entries = store.get_all(limit=1000)
        total = len(entries)
        if total > 0:
            classified = sum(1 for e in entries if e["classification"] != "escalate")
            validated = sum(1 for e in entries if e.get("validated"))
            avg_time = sum(e["execution_time"] for e in entries if e["execution_time"]) / total
            by_cat = {}
            for e in entries:
                by_cat[e["classification"]] = by_cat.get(e["classification"], 0) + 1
            positive_fb = sum(1 for e in entries if e.get("feedback") == 1)
            negative_fb = sum(1 for e in entries if e.get("feedback") == -1)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", total)
                st.metric("Routed", classified)
            with col2:
                st.metric("Validated", validated)
                st.metric("Avg Time", f"{avg_time:.1f}s")
            with col3:
                st.metric("👍 Helpful", positive_fb)
                st.metric("👎 Not", negative_fb)

            st.markdown("#### By Category")
            cat_df = pd.DataFrame(
                [{"Category": k, "Count": v} for k, v in sorted(by_cat.items())]
            )
            st.bar_chart(cat_df.set_index("Category"))
        else:
            st.info("No data yet — start a conversation to see statistics.")

    st.divider()

    with st.expander("About"):
        st.markdown("""
        **Support Triage Crew** v1.1 — Multi-agent AI customer support system.
        CrewAI + Ollama + Streamlit + FastAPI + SQLite.
        """)


def render_sidebar():
    with st.sidebar:
        st.title("🎧 Support Triage")
        st.caption("Multi-Agent Support System")
        st.divider()

        nav = st.radio(
            "Navigation",
            ["💬 Chat", "📋 History", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.divider()
        conversation_count = store.count()
        st.caption(f"🤖 LLM: {LLM_PROVIDER}/{LLM_MODEL}")
        st.caption(f"💬 Conversations: {conversation_count}")
        st.divider()

        if st.button("🆕 New Chat", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.session_state.feedback_sent = set()
            st.rerun()

        if st.button("🗑️ Clear History", use_container_width=True):
            store.clear()
            st.rerun()

    return nav.replace("💬 ", "").replace("📋 ", "").replace("⚙️ ", "")


def main():
    init_state()
    nav = render_sidebar()

    if nav == "Chat":
        render_chat()
    elif nav == "History":
        render_history()
    elif nav == "Settings":
        render_settings()


if __name__ == "__main__":
    main()
