"""
Hashira ATS - AI Resume Intelligence & Job Matching Platform
Streamlit Production-Oriented MVP for Campus Drives & Career Matching
"""
import os
import io
import time
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables
load_dotenv(override=True)

from parser import extract_text
from analyzer import (
    analyze_job_description,
    analyze_resume,
    generate_markdown_report
)
from telegram_bot import (
    test_telegram_connection,
    auto_detect_chat_id,
    get_bot_info,
    format_telegram_candidate_message,
    format_telegram_batch_message,
    send_telegram_message,
    send_telegram_file
)

# Page configuration
st.set_page_config(
    page_title="Hashira ATS — Resume Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Hashira Modern Dark Theme)
st.markdown("""
<style>
    .main {
        background-color: #07111F;
        color: #F8FAFC;
    }
    .stApp {
        background-color: #07111F;
    }
    .metric-card {
        background: linear-gradient(135deg, #0D1B2A 0%, #1B263B 100%);
        border: 1px solid #229ED9;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .score-badge-strong {
        background-color: #064E3B;
        color: #34D399;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .score-badge-good {
        background-color: #1E3A8A;
        color: #60A5FA;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .score-badge-mod {
        background-color: #78350F;
        color: #FBBF24;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .score-badge-low {
        background-color: #7F1D1D;
        color: #F87171;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
    }
    .skill-pill-matched {
        background-color: #064E3B;
        color: #A7F3D0;
        padding: 4px 10px;
        border-radius: 8px;
        margin: 3px;
        font-size: 13px;
        display: inline-block;
        border: 1px solid #059669;
    }
    .skill-pill-missing {
        background-color: #450A0A;
        color: #FECACA;
        padding: 4px 10px;
        border-radius: 8px;
        margin: 3px;
        font-size: 13px;
        display: inline-block;
        border: 1px solid #DC2626;
    }
    .skill-pill-partial {
        background-color: #451A03;
        color: #FED7AA;
        padding: 4px 10px;
        border-radius: 8px;
        margin: 3px;
        font-size: 13px;
        display: inline-block;
        border: 1px solid #D97706;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar: Credentials & System Setup
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=600&auto=format&fit=crop&q=60", use_container_width=True)
    st.title("⚙️ Hashira Config")
    st.caption("AI Resume Intelligence & Campus Drive Evaluation Engine")
    
    st.markdown("---")
    st.subheader("🔑 API Credentials")
    
    env_groq = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY") or ""
    groq_api_key = st.text_input(
        "Groq / xAI Grok API Key",
        value=env_groq,
        type="password",
        help="Supports Groq (gsk_...) or xAI Grok (xai-...). If left blank or invalid, deterministic engine handles scoring safely."
    )
    
    env_tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_bot_token = st.text_input(
        "Telegram Bot Token",
        value=env_tg_token,
        type="password",
        help="Created via @BotFather in Telegram"
    )

    # Inspect bot username if token exists
    bot_username = "your_bot"
    if telegram_bot_token:
        ok_bot, bdata = get_bot_info(telegram_bot_token)
        if ok_bot:
            bot_username = bdata.get("username", "your_bot")
            st.markdown(f"🤖 Bot: [**@{bot_username}**](https://t.me/{bot_username}) *(Click to open)*", unsafe_allow_html=True)

    env_tg_chat = os.getenv("TELEGRAM_CHAT_ID", "")
    if "chat_id_input" not in st.session_state:
        st.session_state["chat_id_input"] = env_tg_chat

    telegram_chat_id = st.text_input(
        "Telegram Chat ID",
        value=st.session_state["chat_id_input"],
        help="Your personal chat ID, group ID, or channel (@channelname)"
    )

    col_tg_act1, col_tg_act2 = st.columns(2)
    with col_tg_act1:
        if st.button("📡 Test Ping", use_container_width=True):
            if telegram_bot_token and telegram_chat_id:
                with st.spinner("Pinging Telegram API..."):
                    ok, msg = test_telegram_connection(telegram_bot_token, telegram_chat_id)
                    if ok:
                        st.success(msg, icon="✅")
                    else:
                        st.error(msg)
            else:
                st.warning("Supply Bot Token and Chat ID.")
                
    with col_tg_act2:
        if st.button("🔍 Auto-Detect ID", use_container_width=True):
            if telegram_bot_token:
                with st.spinner("Checking incoming messages..."):
                    detected, cid, desc = auto_detect_chat_id(telegram_bot_token)
                    if detected:
                        st.session_state["chat_id_input"] = cid
                        st.success(f"✓ {desc}")
                        st.rerun()
                    else:
                        st.warning(desc)
            else:
                st.warning("Enter Bot Token first.")

    st.markdown("---")
    st.subheader("📁 Sample Campus Test Data")
    if st.button("📥 Pre-load Sample Campus Batch", use_container_width=True):
        st.session_state["use_sample_data"] = True
        st.success("Sample Job Description and 3 Resumes loaded!")
        
    st.markdown("---")
    st.caption("🛡️ Hashira ATS • 100% Local File Processing • Free Tools Only")

# Main Page Header
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("# 🤖 HASHIRA ATS")
    st.markdown("##### *AI Resume Intelligence & Multi-Candidate Matching Engine*")
with col_h2:
    st.markdown("<br><span class='score-badge-good'>⚡ CAMPUS DRIVE EDITION</span>", unsafe_allow_html=True)

st.markdown("---")

# Input Section: Tabs for Inputs
tab_upload, tab_text = st.tabs(["📂 File Uploads (PDF / DOCX / TXT)", "📝 Direct Text Paste"])

jd_text = ""
resume_docs = [] # list of (filename, text)

with tab_upload:
    col_jd, col_res = st.columns(2)
    
    with col_jd:
        st.subheader("1️⃣ Job Description (JD)")
        jd_file = st.file_uploader(
            "Upload Job Description",
            type=["pdf", "docx", "txt", "md"],
            help="Upload the target role's job specification."
        )
        if jd_file:
            ok, text, err = extract_text(jd_file, jd_file.name)
            if ok:
                jd_text = text
                st.success(f"✓ Extracted {len(text.split())} words from '{jd_file.name}'")
            else:
                st.error(err)
                
    with col_res:
        st.subheader("2️⃣ Candidate Resumes")
        resume_files = st.file_uploader(
            "Upload Resumes (Single or Multiple)",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            help="Drop 1 or multiple candidate resumes for automated evaluation & ranking."
        )
        if resume_files:
            for rf in resume_files:
                ok, text, err = extract_text(rf, rf.name)
                if ok:
                    resume_docs.append((rf.name, text))
                else:
                    st.error(err)
            if resume_docs:
                st.success(f"✓ Successfully loaded {len(resume_docs)} candidate resume(s)")

with tab_text:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Paste Job Description")
        manual_jd = st.text_area("Paste JD content here", height=220, placeholder="Paste job requirements, required skills, and responsibilities...")
        if manual_jd.strip():
            jd_text = manual_jd.strip()
    with col_t2:
        st.subheader("Paste Candidate Resume")
        manual_resume = st.text_area("Paste Resume text here", height=220, placeholder="Paste candidate resume text, technical skills, experience...")
        if manual_resume.strip():
            resume_docs.append(("Pasted_Candidate_Resume.txt", manual_resume.strip()))

# Check for Sample Data trigger
if st.session_state.get("use_sample_data", False):
    sample_jd_path = "sample_data/sample_jd.txt"
    if os.path.exists(sample_jd_path):
        with open(sample_jd_path, "r", encoding="utf-8") as f:
            jd_text = f.read()
    
    sample_resumes = [
        ("sample_resume_rahul.txt", "sample_data/sample_resume_rahul.txt"),
        ("sample_resume_priya.txt", "sample_data/sample_resume_priya.txt"),
        ("sample_resume_arjun.txt", "sample_data/sample_resume_arjun.txt")
    ]
    resume_docs = []
    for fname, fpath in sample_resumes:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                resume_docs.append((fname, f.read()))
    st.info("Loaded 1 Sample JD ('Backend Developer') and 3 Candidate Resumes (Rahul Kumar, Priya Sharma, Arjun Patel).")

st.markdown("---")

# Execution Button
col_btn1, col_btn2 = st.columns([2, 3])
with col_btn1:
    analyze_clicked = st.button("🚀 ANALYZE & MATCH CANDIDATES", type="primary", use_container_width=True)

if analyze_clicked:
    if not jd_text or len(jd_text.strip()) < 30:
        st.error("⚠️ Please provide a valid Job Description before analyzing.")
    elif not resume_docs:
        st.error("⚠️ Please upload or paste at least 1 candidate resume.")
    else:
        with st.spinner("Parsing Job Description & Analyzing Skill Architecture..."):
            jd_model = analyze_job_description(jd_text)
            
        progress_bar = st.progress(0)
        results = []
        
        for idx, (filename, rtext) in enumerate(resume_docs):
            with st.spinner(f"Evaluating candidate {idx+1}/{len(resume_docs)}: '{filename}'..."):
                res = analyze_resume(
                    resume_text=rtext,
                    filename=filename,
                    jd=jd_model,
                    groq_api_key=groq_api_key
                )
                results.append(res)
            progress_bar.progress((idx + 1) / len(resume_docs))
            
        st.session_state["analysis_results"] = results
        st.session_state["analyzed_jd"] = jd_model
        st.success(f"🎉 Analysis completed for {len(results)} candidate(s)!")

# Results Rendering
if "analysis_results" in st.session_state and st.session_state["analysis_results"]:
    results = st.session_state["analysis_results"]
    jd_model = st.session_state["analyzed_jd"]
    
    # Sort descending by ATS Score
    results = sorted(results, key=lambda c: c.score, reverse=True)
    
    st.markdown("## 📊 Evaluation Results & Leaderboard")
    
    # Batch Leaderboard (when multiple candidates evaluated)
    if len(results) > 1:
        st.markdown(f"### 🏆 Campus Drive Leaderboard — Role: `{jd_model.job_title}`")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        avg_score = round(sum(c.score for c in results) / len(results), 1)
        shortlist_count = len([c for c in results if c.score >= 80])
        train_count = len([c for c in results if c.score < 60])
        
        with m_col1:
            st.metric("Total Candidates", len(results))
        with m_col2:
            st.metric("Average ATS Score", f"{avg_score} / 100")
        with m_col3:
            st.metric("Interview Ready (>=80)", shortlist_count)
        with m_col4:
            st.metric("Needs Training (<60)", train_count)
            
        # Leaderboard Table Cards
        medals = ["🥇", "🥈", "🥉"]
        for rank, c in enumerate(results):
            medal = medals[rank] if rank < 3 else f"#{rank+1}"
            band_class = "score-badge-strong" if c.score >= 80 else ("score-badge-good" if c.score >= 65 else ("score-badge-mod" if c.score >= 50 else "score-badge-low"))
            
            with st.container():
                c_col1, c_col2, c_col3, c_col4 = st.columns([1, 4, 3, 2])
                with c_col1:
                    st.markdown(f"### {medal}")
                with c_col2:
                    st.markdown(f"**{c.candidate_name}** (`{c.filename}`)")
                    st.caption(f"Matched Skills: {', '.join(c.matched_skills[:5]) or 'None'}")
                with c_col3:
                    st.progress(c.score / 100.0)
                    st.caption(f"Score: {c.score}/100")
                with c_col4:
                    st.markdown(f"<span class='{band_class}'>{c.compatibility_band}</span>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)
                
        # Batch Telegram Delivery Option
        if telegram_bot_token and telegram_chat_id:
            if st.button("📤 Send Campus Drive Batch Summary to Telegram", key="btn_send_batch_tg"):
                batch_msg = format_telegram_batch_message(results, jd_model.job_title)
                ok, res_msg = send_telegram_message(batch_msg, telegram_bot_token, telegram_chat_id)
                if ok:
                    st.success("✓ Batch summary posted to Telegram!")
                else:
                    st.error(res_msg)
        else:
            st.info("💡 Set Telegram credentials in sidebar to transmit the batch leaderboard directly to your channel.")
            
        st.markdown("---")
        
    # Candidate Deep Dive Selector
    candidate_options = [f"{c.candidate_name} ({c.score}/100 - {c.compatibility_band})" for c in results]
    selected_idx = st.selectbox(
        "🔎 Select Candidate for In-Depth ATS Intelligence & Improvement Roadmap:",
        range(len(candidate_options)),
        format_func=lambda i: candidate_options[i]
    )
    
    c = results[selected_idx]
    
    # Candidate Hero Header
    c_hero1, c_hero2 = st.columns([3, 1])
    with c_hero1:
        st.markdown(f"### 👤 {c.candidate_name}")
        st.caption(f"File: `{c.filename}` • Role: **{c.target_role}**")
    with c_hero2:
        band_class = "score-badge-strong" if c.score >= 80 else ("score-badge-good" if c.score >= 65 else ("score-badge-mod" if c.score >= 50 else "score-badge-low"))
        st.markdown(f"<div style='text-align: right;'><span class='{band_class}' style='font-size: 16px;'>{c.score} / 100 • {c.compatibility_band}</span></div>", unsafe_allow_html=True)

    # Detailed Score Breakdown Bars
    st.markdown("#### 📈 Explainable ATS Score Dimensions")
    sb = c.score_breakdown
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"**Required Skills Coverage (30% weight):** {sb.required_skills}/30")
        st.progress(sb.required_skills / 30.0)
        
        st.markdown(f"**Technical Skill Match (20% weight):** {sb.technical_skills}/20")
        st.progress(sb.technical_skills / 20.0)
        
        st.markdown(f"**Semantic JD Relevance (15% weight):** {sb.semantic_relevance}/15")
        st.progress(sb.semantic_relevance / 15.0)
        
    with col_d2:
        st.markdown(f"**Experience / Role Alignment (10% weight):** {sb.experience_match}/10")
        st.progress(sb.experience_match / 10.0)
        
        st.markdown(f"**Keyword Coverage (10% weight):** {sb.keyword_coverage}/10")
        st.progress(sb.keyword_coverage / 10.0)
        
        st.markdown(f"**Projects & Evidence (10% weight):** {sb.projects_evidence}/10")
        st.progress(sb.projects_evidence / 10.0)
        
        st.markdown(f"**ATS Format & Readability (5% weight):** {sb.ats_readability}/5")
        st.progress(sb.ats_readability / 5.0)

    st.markdown("---")
    
    # Skills Matrix
    st.markdown("#### 🎯 Technical Skills Alignment")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.markdown("##### ✅ Matched in Resume")
        if c.matched_skills:
            html_pills = "".join([f"<span class='skill-pill-matched'>{s}</span>" for s in c.matched_skills])
            st.markdown(html_pills, unsafe_allow_html=True)
        else:
            st.write("No exact skills detected.")
            
    with col_s2:
        st.markdown("##### ⚠️ Partial / Preferred Gaps")
        if c.partial_skills:
            html_pills = "".join([f"<span class='skill-pill-partial'>{s}</span>" for s in c.partial_skills])
            st.markdown(html_pills, unsafe_allow_html=True)
        else:
            st.write("None identified.")
            
    with col_s3:
        st.markdown("##### ❌ Missing / Required by JD")
        if c.missing_skills:
            html_pills = "".join([f"<span class='skill-pill-missing'>{s}</span>" for s in c.missing_skills])
            st.markdown(html_pills, unsafe_allow_html=True)
        else:
            st.write("All required skills found!")

    st.markdown("---")

    # Strengths, Weaknesses, and Improvements
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.markdown("#### 💡 Candidate Strengths")
        for s in c.strengths:
            st.markdown(f"- ✅ {s}")
            
        st.markdown("#### ⚠️ Potential Gaps")
        for w in c.weaknesses:
            st.markdown(f"- ⚠️ {w}")
            
    with col_w2:
        st.markdown("#### 🔥 High-Impact Resume Improvements")
        for i, imp in enumerate(c.improvements):
            st.markdown(f"**{i+1}.** {imp}")
            
        if c.ats_formatting_issues:
            st.markdown("#### 📋 ATS Format Diagnostics")
            for iss in c.ats_formatting_issues:
                st.warning(f"• {iss}")

    st.markdown("---")

    # 7-Day Sprint Roadmap & Recommended Projects
    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        st.markdown("#### 📅 7-Day Skill Gap Closure Sprint")
        for item in c.learning_roadmap:
            with st.expander(f"**{item['day']}: {item['focus']}**"):
                st.write(item["task"])
                
    with col_p2:
        st.markdown("#### 🛠️ Recommended Portfolio Projects")
        for proj in c.recommended_projects:
            st.info(f"📌 {proj}")
            
        st.markdown("#### 📚 Curated Free Resources")
        for res in c.free_resources:
            st.markdown(f"- **{res['skill']}**: [{res['title']}]({res['url']}) *({res['provider']})*")

    st.markdown("---")

    # Final Verdict & Telegram Dispatch
    st.markdown("#### 🏁 Final Hiring Readiness Verdict")
    st.info(f"**Conclusion:** {c.final_verdict}")
    
    # Save Report & Dispatch
    report_file_path = generate_markdown_report(c)
    
    col_tg1, col_tg2 = st.columns(2)
    with col_tg1:
        # Download Markdown Report
        with open(report_file_path, "r", encoding="utf-8") as rf:
            rep_text = rf.read()
        st.download_button(
            label=f"💾 Download Full Markdown Report ({c.candidate_name})",
            data=rep_text,
            file_name=os.path.basename(report_file_path),
            mime="text/markdown",
            use_container_width=True
        )
        
    with col_tg2:
        # Telegram Transmission
        if st.button(f"📱 Send {c.candidate_name}'s Report to Telegram", type="secondary", use_container_width=True):
            if not telegram_bot_token or not telegram_chat_id:
                st.error("⚠️ Please configure Telegram Bot Token and Chat ID in the sidebar.")
            else:
                with st.spinner("Dispatching report to Telegram..."):
                    card_msg = format_telegram_candidate_message(c)
                    ok_msg, status_msg = send_telegram_message(card_msg, telegram_bot_token, telegram_chat_id)
                    
                    caption = f"📄 Complete Hashira ATS Report for {c.candidate_name}"
                    ok_file, status_file = send_telegram_file(report_file_path, caption, telegram_bot_token, telegram_chat_id)
                    
                    if ok_msg:
                        st.success(f"✓ Successfully sent candidate evaluation to Telegram! ({status_msg})")
                        if ok_file:
                            st.caption("✓ Attached markdown report file sent to chat.")
                    else:
                        st.error(f"Failed to send to Telegram: {status_msg}")

st.markdown("<br><br><div style='text-align: center; color: #64748B;'>Hashira ATS • AI Resume Intelligence & Campus Drive Automation • Built with Antigravity</div>", unsafe_allow_html=True)
