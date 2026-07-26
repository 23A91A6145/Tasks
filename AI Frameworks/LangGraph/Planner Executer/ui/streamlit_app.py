import time
import requests
import streamlit as st

API_BASE = "http://localhost:8000/api"

st.set_page_config(
    page_title="Planner Executor",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Two-Agent Planner + Executor")
st.caption("Groq (planner) + Ollama (executor) + Auto-Replanning")

if "job_id" not in st.session_state:
    st.session_state.job_id = None
if "status" not in st.session_state:
    st.session_state.status = None

# --- Connection Check ---
def check_api():
    try:
        r = requests.get(f"{API_BASE.replace('/api', '')}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

api_ok = check_api()
if not api_ok:
    st.warning("⚠️ API server not running. Start it with: `uvicorn api.app:app --reload --port 8000`")

# --- Task Input ---
st.markdown("---")
st.subheader("📋 Task Input")

examples = [
    "Explain quantum computing in 3 steps",
    "Compare Python and Rust in 3 points",
    "Write a haiku about programming",
    "List 3 benefits of exercise",
]

col_input, col_examples = st.columns([3, 1])
with col_input:
    task = st.text_area(
        "Enter your task",
        placeholder="Type a task or pick an example →",
        height=80,
    )
with col_examples:
    st.markdown("**Examples:**")
    for ex in examples:
        if st.button(ex, key=f"ex_{ex[:20]}", use_container_width=True):
            task = ex
            st.rerun()

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    run_btn = st.button("▶ Run", type="primary", use_container_width=True, disabled=not api_ok)
with col2:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.job_id = None
        st.session_state.status = None
        st.rerun()
with col3:
    if st.session_state.job_id:
        status_color = {"completed": "✅", "failed": "❌", "pending": "⏳"}.get(
            st.session_state.status, "🔄"
        )
        st.info(f"{status_color} Job: `{st.session_state.job_id}`")

# --- Run ---
if run_btn and task.strip():
    if len(task.strip()) < 5:
        st.error("Task must be at least 5 characters.")
    else:
        try:
            resp = requests.post(f"{API_BASE}/run", json={"task": task.strip()}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            st.session_state.job_id = data["job_id"]
            st.session_state.status = "pending"
            st.rerun()
        except requests.ConnectionError:
            st.error("Cannot connect to API. Is `uvicorn api.app:app --port 8000` running?")
        except Exception as e:
            st.error(f"Error: {e}")

# --- Status Polling ---
if st.session_state.job_id:
    st.markdown("---")
    status_ph = st.empty()
    progress_ph = st.empty()
    plan_ph = st.empty()
    results_ph = st.empty()
    footer_ph = st.empty()

    job_id = st.session_state.job_id
    done = False
    elapsed = 0
    max_wait = 1800  # 30 minutes

    while elapsed < max_wait:
        try:
            s_resp = requests.get(f"{API_BASE}/status/{job_id}", timeout=5)
            s_resp.raise_for_status()
            s = s_resp.json()
        except Exception:
            time.sleep(2)
            elapsed += 2
            continue

        status = s["status"]
        st.session_state.status = status
        total = max(s["steps_total"], 1)
        completed = s["steps_completed"]
        pct = completed / total

        status_ph.subheader("📊 Progress")
        status_icons = {
            "pending": "⏳",
            "planning": "🧠",
            "executing": "⚡",
            "replanning": "🔄",
            "completed": "✅",
            "failed": "❌",
        }
        icon = status_icons.get(status, "❓")
        progress_ph.progress(
            pct,
            text=f"{icon} {status.title()} — Step {completed}/{total} ({elapsed}s elapsed)",
        )

        plan_ph.subheader("📝 Plan")
        plan_lines = s.get("plan", [])
        current = s.get("current_step")
        for i, step in enumerate(plan_lines, 1):
            if step.startswith("[REPLANNED]"):
                step_clean = step.replace("[REPLANNED] ", "")
                plan_ph.markdown(f"  🔄 **(replan)** {step_clean}")
            elif status == "completed" and i <= completed:
                plan_ph.markdown(f"  ✅ {step}")
            elif step == current:
                plan_ph.markdown(f"  🔄 **{step}** ← current")
            elif i <= completed:
                plan_ph.markdown(f"  ✅ {step}")
            else:
                plan_ph.markdown(f"  ⏳ {step}")

        try:
            l_resp = requests.get(f"{API_BASE}/logs/{job_id}", timeout=5)
            l_resp.raise_for_status()
            logs = l_resp.json().get("results", [])
        except Exception:
            logs = []

        if logs:
            results_ph.subheader("📜 Results")
            for r in logs:
                r_icon = "✅" if r["status"] == "completed" else "❌"
                with results_ph.expander(
                    f"{r_icon} {r['step']}", expanded=(r["status"] != "completed")
                ):
                    if r["status"] == "completed":
                        st.markdown(r["result"])
                    else:
                        st.error(f"Error: {r.get('error', 'Unknown')}")

        footer_ph.caption(
            f"Job: `{s['job_id']}` | Created: {s['created_at'][:19]} | Updated: {s['updated_at'][:19]}"
        )

        if status in ("completed", "failed"):
            done = True
            if status == "completed":
                status_ph.success("Pipeline completed successfully!")
            else:
                status_ph.error(f"Pipeline failed: {s.get('error', 'Unknown error')}")
            break

        time.sleep(2)
        elapsed += 2

    if not done:
        status_ph.warning(f"Timed out after {max_wait}s. The job may still be running in the background.")
