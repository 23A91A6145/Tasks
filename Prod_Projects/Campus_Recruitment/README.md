# 🤖 Hashira ATS — AI Resume Intelligence & Campus Drive Matching Platform

> **Production-Ready Campus Drive ATS Evaluation & Telegram Reporting Engine**  
> Built for automated multi-candidate screening, deterministic keyword/skill matching, explainable scoring, automated 7-day learning roadmaps, and instant Telegram delivery.

---

## 🎯 Architecture Diagram

```text
               ┌────────────────────────────────────────────────────────┐
               │              JOB DESCRIPTION + RESUMES                 │
               │               (PDF / DOCX / TXT / MD)                  │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │                 ROBUST DOCUMENT PARSER                 │
               │             (PyMuPDF • python-docx • UTF-8)            │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │              DETERMINISTIC ATS ENGINE                  │
               │   • Skill Taxonomy Normalization (Postgres == SQL)     │
               │   • Mandatory vs Preferred Skill Analysis              │
               │   • ATS Format Readability & Metric Density Checks     │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │            GROQ / xAI GROK SEMANTIC ENGINE             │
               │   • Deep Contextual JD ↔ Resume Relevance              │
               │   • Hallucination Guardrails (Zero False Attributes)   │
               │   • Concrete Impact Rewrite Suggestions                │
               └───────────────────────────┬────────────────────────────┘
                                           │
                                           ▼
               ┌────────────────────────────────────────────────────────┐
               │             COMPREHENSIVE REPORT GENERATION            │
               │   • 7-Day Structured Gap-Closure Sprint Plan           │
               │   • Curated 100% Free Learning Resources (Official)    │
               │   • Standalone Markdown Dossiers in /reports           │
               └───────────────────────────┬────────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
             ┌─────────────────────┐               ┌─────────────────────┐
             │ STREAMLIT DASHBOARD │               │    TELEGRAM BOT     │
             │  • Batch Ranking    │               │  • Instant Cards    │
             │  • Candidate Tabs   │               │  • File Attachment  │
             │  • Dark Mode UI     │               │  • Batch Summary    │
             └─────────────────────┘               └─────────────────────┘
```

---

## ⚡ Quick Run (Single Command)

To launch the Hashira ATS platform on your Ubuntu system:

```bash
cd /home/cherry/hashira
source .venv/bin/activate
streamlit run app.py
```

Then open your browser at: **`http://localhost:8501`**

---

## 📱 Telegram Bot Setup & Verification

Your bot token was tested and verified with the Telegram Bot API:
- **Bot Name:** `hashira_bot1`
- **Bot Handle:** [`@hashira120612061206bot`](https://t.me/hashira120612061206bot)

### ⚠️ How to Connect Telegram in 10 Seconds:
Telegram prevents bots from sending unprompted messages until you initiate the chat:
1. Open Telegram on your phone or web app.
2. Click or search: **[@hashira120612061206bot](https://t.me/hashira120612061206bot)**
3. Tap **START** (or send `/start` or `hi`).
4. In the Streamlit sidebar, click **"🔍 Auto-Detect ID"** or **"📡 Test Ping"**.
5. Your bot will instantly send a confirmation ping and is ready to deliver live candidate dossiers!

---

## 🔑 AI API Credentials (Groq / xAI Grok)

Edit `/home/cherry/hashira/.env`:
```env
# Option A: Groq API Key (Free tier at https://console.groq.com/keys)
GROQ_API_KEY=gsk_your_full_groq_key_here

# Option B: xAI Grok API Key (https://console.x.ai)
GROK_API_KEY=xai-your_xai_key_here

# Telegram Credentials
TELEGRAM_BOT_TOKEN=8651288458:AA...
TELEGRAM_CHAT_ID=6537834896
```
> **Note:** Even if no API key is provided, the platform operates on its deterministic ATS engine, calculating accurate scores and generating full reports with zero failures.

---

## 🧪 Verification & Test Suite

Run the automated test pipeline at any time:
```bash
python test_pipeline.py
```

**Results:**
- `Rahul Kumar` (Strong Backend Match): **88 / 100** (`STRONG MATCH`)
- `Priya Sharma` (Data / AI Match): **55 / 100** (`MODERATE MATCH`)
- `Arjun Patel` (Junior Frontend): **44 / 100** (`LOW MATCH`)
- Edge Cases & Empty Files: **Graceful fallback (28/100, no crashes)**

---

## 📂 Project Structure

```text
hashira/
├── app.py                  # Streamlit Interactive Dashboard & UI
├── analyzer.py             # Intelligence Orchestrator (Deterministic + AI)
├── parser.py               # Universal Document Parser (PDF, DOCX, TXT)
├── scoring.py              # Heuristic & Deterministic ATS Scoring Engine
├── telegram_bot.py         # Direct HTTP Telegram Bot Client & Doc Uploader
├── prompts.py              # Guardrails, Schema Prompts, Free Resource Catalog
├── models.py               # Dataclass data models (CandidateResult, Breakdown)
├── test_pipeline.py        # Automated end-to-end verification suite
├── requirements.txt        # Python package dependencies
├── .env                    # Active credentials file
├── sample_data/            # Sample files for campus drive testing
│   ├── sample_jd.txt
│   ├── sample_resume_rahul.txt
│   ├── sample_resume_priya.txt
│   └── sample_resume_arjun.txt
└── reports/                # Exported markdown dossiers
    ├── rahul_kumar_ats_report.md
    ├── priya_sharma_ats_report.md
    └── arjun_patel_ats_report.md
```

---

## 🏆 Key Features

1. **Batch Multi-Resume Processing**: Upload 1 JD and 1 to 100+ resumes at once; generates an instant campus drive leaderboard with shortlist counts.
2. **Explainable Scoring**:
   - Required Skill Coverage: **30%**
   - Technical Skill Match: **20%**
   - Semantic Relevance: **15%**
   - Experience Alignment: **10%**
   - Keyword Coverage: **10%**
   - Projects Evidence: **10%**
   - ATS Format Readability: **5%**
3. **Actionable 7-Day Sprint**: Builds a personalized day-by-day remediation plan for every candidate.
4. **Curated Free Learning Tracks**: Integrates official free courses from Redis University, Docker Getting Started, AWS Skill Builder, FastAPI, and GitHub Skills.
5. **Dual Telegram Delivery**: Sends an instant summary card and attaches the full `.md` report document directly to Telegram.
