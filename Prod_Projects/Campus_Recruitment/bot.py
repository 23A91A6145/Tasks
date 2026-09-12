"""
Hashira ATS - Master Telegram Bot Application
Complete backend running 100% inside Telegram without any localhost browser dashboard.
"""
import os
import io
import html
import logging
from typing import Optional
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import (
    TELEGRAM_BOT_TOKEN,
    GROQ_API_KEY,
    BOT_NAME,
    BOT_VERSION
)
from models import (
    SessionState,
    UploadedResume,
    CandidateResult
)
from session_manager import session_manager
from parser import extract_text, detect_candidate_name
from analyzer import analyze_job_description, analyze_resume
from report_generator import (
    generate_candidate_report_md,
    generate_batch_report_md,
    generate_ranking_csv
)
from telegram_views import (
    format_welcome_message,
    format_new_analysis_prompt,
    format_jd_received,
    format_resume_received,
    format_workspace_status,
    format_candidate_ats_card,
    format_improvement_plan,
    format_learning_roadmap,
    format_courses_and_conclusion,
    format_ranking_leaderboard,
    format_candidate_comparison
)
from qna_engine import answer_user_query

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Standard Keyboard for quick Telegram interaction
MAIN_KEYBOARD = [
    [KeyboardButton("/new"), KeyboardButton("/status")],
    [KeyboardButton("/analyze"), KeyboardButton("/report")],
    [KeyboardButton("/compare"), KeyboardButton("/help")]
]
REPLY_MARKUP = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

async def safe_reply(update: Update, text: str, reply_markup=REPLY_MARKUP):
    """Safely send HTML formatted message with fallback to plain text if syntax error occurs."""
    try:
        await update.effective_message.reply_text(
            text,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.warning(f"HTML send failed ({e}); falling back to plain text.")
        # Strip simple tags or send raw
        clean_text = text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
        clean_text = clean_text.replace("<code>", "").replace("</code>", "").replace("<pre>", "").replace("</pre>", "")
        await update.effective_message.reply_text(
            clean_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

# Command Handlers
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    welcome_text = format_welcome_message()
    await safe_reply(update, welcome_text)

async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /new command - starts new analysis cycle."""
    chat_id = update.effective_chat.id
    session_manager.reset_session(chat_id)
    session_manager.set_state(chat_id, SessionState.WAITING_FOR_JD)
    prompt = format_new_analysis_prompt()
    await safe_reply(update, prompt)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /status command - displays current session status."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    
    role = session.current_jd.job_title if session.current_jd else ""
    resumes_info = [f"{r.filename} ({r.candidate_name})" for r in session.resumes]
    is_analyzed = len(session.analysis_results) > 0
    
    status_text = format_workspace_status(
        role=role,
        resume_count=len(session.resumes),
        resumes_info=resumes_info,
        is_analyzed=is_analyzed
    )
    await safe_reply(update, status_text)

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /clear command - resets workspace."""
    chat_id = update.effective_chat.id
    session_manager.reset_session(chat_id)
    await safe_reply(update, "🧹 <b>Workspace reset.</b>\nSend /new to start a new analysis.")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    help_text = """ℹ️ <b>Hashira ATS — Quick Help Guide</b>

<b>Standard Workflow:</b>
1️⃣ <b>/new</b> — Begin a new ATS evaluation session.
2️⃣ <b>Upload Job Description</b> — Send a PDF, DOCX, or TXT file, or paste text.
3️⃣ <b>Upload Resumes</b> — Send 1 or multiple candidate resumes.
4️⃣ <b>/analyze</b> — Execute ATS scoring, skill matching, roadmap, and ranking.
5️⃣ <b>Ask Q&A</b> — Ask conversational questions directly:
   • <i>"Why did Candidate 1 score higher?"</i>
   • <i>"What skills is Rahul missing?"</i>
   • <i>"How can I reach 90?"</i>
   • <i>"What projects should Priya build?"</i>
6️⃣ <b>/report</b> — Re-download full 14-section Markdown report & ranking CSV.
7️⃣ <b>/compare</b> — Side-by-side candidate comparison matrix.

<i>Everything operates 100% inside Telegram without opening any browser.</i>"""
    await safe_reply(update, help_text)

async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /analyze command - runs ATS evaluation on uploaded resumes."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    
    if not session.current_jd:
        await safe_reply(update, "⚠️ <b>Missing Job Description.</b>\nPlease send /new and upload a Job Description first.")
        return
        
    if not session.resumes:
        await safe_reply(update, "⚠️ <b>No resumes uploaded.</b>\nPlease upload at least 1 resume (PDF, DOCX, TXT) before analyzing.")
        return

    session_manager.set_state(chat_id, SessionState.ANALYZING)
    res_count = len(session.resumes)
    role_name = session.current_jd.job_title
    
    status_msg = await update.effective_message.reply_text(
        f"⏳ <b>Analyzing {res_count} resume(s) against '{role_name}'...</b>\n<i>Running Deterministic ATS Rubric + Groq LLaMA-3.3-70B AI...</i>",
        parse_mode="HTML"
    )
    
    results = []
    for r in session.resumes:
        try:
            cand_res = analyze_resume(
                resume_text=r.raw_text,
                filename=r.filename,
                jd=session.current_jd,
                groq_api_key=GROQ_API_KEY
            )
            results.append(cand_res)
        except Exception as e:
            logger.error(f"Error analyzing {r.filename}: {e}")

    session_manager.set_analysis_results(chat_id, results)

    # 1. If Single Candidate Analysis
    if len(results) == 1:
        res = results[0]
        # Card 1: Score & Skills
        card_text = format_candidate_ats_card(res)
        await safe_reply(update, card_text)
        
        # Card 2: Improvement Plan
        imp_text = format_improvement_plan(res)
        await safe_reply(update, imp_text)
        
        # Card 3: Learning Roadmap
        roadmap_text = format_learning_roadmap(res)
        await safe_reply(update, roadmap_text)
        
        # Card 4: Recommended Courses & Verdict
        verdict_text = format_courses_and_conclusion(res)
        await safe_reply(update, verdict_text)
        
        # Generate & Send Full 14-Section Markdown Report Attachment
        rep_path = generate_candidate_report_md(res)
        if os.path.exists(rep_path):
            with open(rep_path, "rb") as doc:
                await update.effective_message.reply_document(
                    document=doc,
                    filename=os.path.basename(rep_path),
                    caption=f"📄 Full 14-Section ATS Report for {res.candidate_name}"
                )

    # 2. If Multiple Candidate Analysis (Campus / Batch Drive)
    else:
        # Leaderboard Card
        ranking_text = format_ranking_leaderboard(results, role_name)
        await safe_reply(update, ranking_text)
        
        # Show Top Candidate Details
        top_cand = sorted(results, key=lambda c: c.score, reverse=True)[0]
        top_card = format_candidate_ats_card(top_cand)
        await safe_reply(update, f"🌟 <b>Top Candidate Spotlight:</b>\n\n{top_card}")
        
        top_imp = format_improvement_plan(top_cand)
        await safe_reply(update, top_imp)
        
        # Generate Batch Report (.md) and Ranking CSV
        batch_rep_path = generate_batch_report_md(results, session.current_jd)
        ranking_csv_path = generate_ranking_csv(results)
        
        if os.path.exists(batch_rep_path):
            with open(batch_rep_path, "rb") as doc:
                await update.effective_message.reply_document(
                    document=doc,
                    filename="hashira_ats_report.md",
                    caption=f"📊 Batch ATS Intelligence Report ({len(results)} Candidates)"
                )
                
        if os.path.exists(ranking_csv_path):
            with open(ranking_csv_path, "rb") as doc:
                await update.effective_message.reply_document(
                    document=doc,
                    filename="candidate_ranking.csv",
                    caption="📈 Candidate Leaderboard Ranking (CSV)"
                )

async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /report command - generates and sends reports."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    
    if not session.analysis_results:
        await safe_reply(update, "⚠️ No analysis results found. Please run /analyze first.")
        return
        
    if len(session.analysis_results) == 1:
        res = session.analysis_results[0]
        rep_path = generate_candidate_report_md(res)
        with open(rep_path, "rb") as doc:
            await update.effective_message.reply_document(
                document=doc,
                filename=os.path.basename(rep_path),
                caption=f"📄 Full 14-Section ATS Report for {res.candidate_name}"
            )
    else:
        batch_rep_path = generate_batch_report_md(session.analysis_results, session.current_jd)
        ranking_csv_path = generate_ranking_csv(session.analysis_results)
        
        with open(batch_rep_path, "rb") as doc:
            await update.effective_message.reply_document(
                document=doc,
                filename="hashira_ats_report.md",
                caption="📊 Batch ATS Intelligence Report"
            )
        with open(ranking_csv_path, "rb") as doc:
            await update.effective_message.reply_document(
                document=doc,
                filename="candidate_ranking.csv",
                caption="📈 Candidate Leaderboard CSV"
            )

async def cmd_compare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /compare command."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    
    if not session.analysis_results or len(session.analysis_results) < 2:
        await safe_reply(update, "⚠️ Please upload at least 2 resumes and run /analyze to compare candidates.")
        return
        
    comp_text = format_candidate_comparison(session.analysis_results)
    await safe_reply(update, comp_text)

# Document Upload Handler (PDF, DOCX, TXT)
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles document uploads (JD or Resumes)."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    doc = update.effective_message.document
    
    filename = doc.file_name or "document.pdf"
    lower_name = filename.lower()
    
    if not (lower_name.endswith(".pdf") or lower_name.endswith(".docx") or lower_name.endswith(".txt") or lower_name.endswith(".md")):
        await safe_reply(update, f"⚠️ Unsupported file type: <code>{filename}</code>.\nPlease upload a <b>PDF</b>, <b>DOCX</b>, or <b>TXT</b> file.")
        return

    # Download document from Telegram
    try:
        tg_file = await doc.get_file()
        file_bytes = await tg_file.download_as_bytearray()
        stream = io.BytesIO(file_bytes)
        
        ok, text, err = extract_text(stream, filename)
        if not ok or not text:
            await safe_reply(update, f"❌ Failed to extract text from <code>{filename}</code>: {err or 'Empty file'}")
            return
            
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        await safe_reply(update, f"❌ Download error: {str(e)}")
        return

    # Case A: Waiting for Job Description or no JD loaded yet
    if session.state == SessionState.WAITING_FOR_JD or session.current_jd is None:
        jd = analyze_job_description(text)
        session_manager.set_jd(chat_id, jd, raw_text=text, filename=filename)
        reply_msg = format_jd_received(jd)
        await safe_reply(update, reply_msg)
        return

    # Case B: Already have JD -> Treat as Candidate Resume
    cand_name = detect_candidate_name(text, filename)
    resume = UploadedResume(
        filename=filename,
        candidate_name=cand_name,
        raw_text=text,
        doc_id=doc.file_id
    )
    count = session_manager.add_resume(chat_id, resume)
    role_title = session.current_jd.job_title if session.current_jd else "Target Role"
    
    reply_msg = format_resume_received(
        count=count,
        filename=filename,
        candidate_name=cand_name,
        target_role=role_title
    )
    await safe_reply(update, reply_msg)

# Text Message Handler (JD pasting or Conversational Q&A)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages (pasted JD, pasted resume, or conversational Q&A)."""
    chat_id = update.effective_chat.id
    session = session_manager.get_session(chat_id)
    text = update.effective_message.text.strip()
    
    # Check if text is a pasted Job Description
    is_potential_jd = any(k in text.lower() for k in ["job title", "role", "requirements", "responsibilities", "qualifications", "experience:"])
    
    if session.state == SessionState.WAITING_FOR_JD or (session.current_jd is None and is_potential_jd):
        jd = analyze_job_description(text)
        session_manager.set_jd(chat_id, jd, raw_text=text, filename="Pasted_Job_Description.txt")
        reply_msg = format_jd_received(jd)
        await safe_reply(update, reply_msg)
        return

    # If in Q&A mode (analysis completed), process conversational questions
    if session.state == SessionState.ANALYSIS_COMPLETE:
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        answer = answer_user_query(text, session, groq_api_key=GROQ_API_KEY)
        await safe_reply(update, answer)
        return

    # If waiting for resumes and text looks like a resume
    is_potential_resume = any(k in text.lower() for k in ["education", "experience", "skills", "projects", "certifications"]) and len(text.split()) > 40
    if session.state in [SessionState.WAITING_FOR_RESUMES, SessionState.RESUMES_RECEIVED] and is_potential_resume:
        cand_name = detect_candidate_name(text, "Pasted_Resume.txt")
        resume = UploadedResume(
            filename="Pasted_Resume.txt",
            candidate_name=cand_name,
            raw_text=text
        )
        count = session_manager.add_resume(chat_id, resume)
        role_title = session.current_jd.job_title if session.current_jd else "Target Role"
        reply_msg = format_resume_received(count, "Pasted_Resume.txt", cand_name, role_title)
        await safe_reply(update, reply_msg)
        return

    # Otherwise guide the user
    await safe_reply(
        update,
        "💡 <b>Welcome to Hashira ATS!</b>\n\n"
        "• Send /new to begin evaluating resumes against a Job Description.\n"
        "• Upload a <b>PDF</b>, <b>DOCX</b>, or <b>TXT</b> resume.\n"
        "• Send /status to view your current workspace.\n"
        "• Send /help for full instructions."
    )

def main():
    """Start Telegram Bot application polling."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is missing in .env")
        return
        
    print("==================================================")
    print(f"🚀 Starting {BOT_NAME} v{BOT_VERSION} Telegram Bot...")
    print(f"• Pure Telegram Interface: No browser or localhost UI required")
    print(f"• Deterministic ATS Engine + Groq AI Analysis")
    print("==================================================")

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("new", cmd_new))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("analyze", cmd_analyze))
    application.add_handler(CommandHandler("report", cmd_report))
    application.add_handler(CommandHandler("compare", cmd_compare))
    application.add_handler(CommandHandler("clear", cmd_clear))
    application.add_handler(CommandHandler("help", cmd_help))

    # Documents
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Hashira ATS Bot is running and listening for Telegram events!")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
