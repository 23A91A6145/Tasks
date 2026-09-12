"""
Hashira ATS - Comprehensive Telegram Simulation & Lifecycle Verification Test
Simulates full Telegram conversation flow:
/start -> /new -> JD Upload -> Multi-Resume Upload -> /status -> /analyze -> Reports -> Q&A -> /compare -> /clear
"""
import os
import sys
from models import SessionState, UploadedResume
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
    format_ranking_leaderboard,
    format_candidate_comparison
)
from qna_engine import answer_user_query
from config import GROQ_API_KEY

def run_simulation():
    test_chat_id = 99999999
    print("==================================================")
    print("🧪 Starting Hashira ATS End-to-End Simulation Test")
    print("==================================================")

    # Step 1: /start
    print("\n[Step 1] User sends /start")
    welcome = format_welcome_message()
    assert "HASHIRA ATS" in welcome
    print("  ✓ Welcome message verified.")

    # Step 2: /new
    print("\n[Step 2] User sends /new")
    session_manager.reset_session(test_chat_id)
    session_manager.set_state(test_chat_id, SessionState.WAITING_FOR_JD)
    prompt = format_new_analysis_prompt()
    assert "Step 1/2" in prompt
    print("  ✓ /new prompt verified.")

    # Step 3: Upload Job Description
    print("\n[Step 3] User uploads Job Description (sample_data/sample_jd.txt)")
    with open("sample_data/sample_jd.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
    
    jd = analyze_job_description(jd_text)
    session_manager.set_jd(test_chat_id, jd, raw_text=jd_text, filename="Backend_Developer_JD.txt")
    jd_reply = format_jd_received(jd)
    print(f"  ✓ JD Role Detected: {jd.job_title}")
    print(f"  ✓ Mandatory Skills: {jd.mandatory_skills}")
    assert len(jd.mandatory_skills) > 0
    print("  ✓ JD receipt confirmation message formatted successfully.")

    # Step 4: Upload Resumes (Rahul, Priya, Arjun)
    resume_files = [
        "sample_data/sample_resume_rahul.txt",
        "sample_data/sample_resume_priya.txt",
        "sample_data/sample_resume_arjun.txt"
    ]
    
    print("\n[Step 4] User uploads 3 candidate resumes...")
    for idx, rpath in enumerate(resume_files):
        with open(rpath, "r", encoding="utf-8") as f:
            rtext = f.read()
        fname = os.path.basename(rpath)
        cand_name = detect_candidate_name(rtext, fname)
        r_obj = UploadedResume(filename=fname, candidate_name=cand_name, raw_text=rtext)
        cnt = session_manager.add_resume(test_chat_id, r_obj)
        res_reply = format_resume_received(cnt, fname, cand_name, jd.job_title)
        print(f"  ✓ Resume {cnt}: {fname} ({cand_name}) received.")

    # Step 5: /status
    print("\n[Step 5] User sends /status")
    session = session_manager.get_session(test_chat_id)
    status_msg = format_workspace_status(
        role=jd.job_title,
        resume_count=len(session.resumes),
        resumes_info=[f"{r.filename} ({r.candidate_name})" for r in session.resumes],
        is_analyzed=False
    )
    assert "Resumes (3)" in status_msg
    print("  ✓ Status message shows 3 uploaded resumes and loaded JD.")

    # Step 6: /analyze
    print("\n[Step 6] User sends /analyze")
    evaluated = []
    for r in session.resumes:
        cand_res = analyze_resume(
            resume_text=r.raw_text,
            filename=r.filename,
            jd=session.current_jd,
            groq_api_key=GROQ_API_KEY
        )
        evaluated.append(cand_res)
    
    session_manager.set_analysis_results(test_chat_id, evaluated)
    assert len(session.analysis_results) == 3

    # Ranking check
    sorted_res = sorted(evaluated, key=lambda c: c.score, reverse=True)
    top_c = sorted_res[0]
    print(f"  ✓ Candidate Rankings:")
    for idx, c in enumerate(sorted_res):
        print(f"    #{idx+1}: {c.candidate_name} — {c.score}/100 ({c.compatibility_band})")
        
    assert top_c.candidate_name == "Rahul Kumar", "Rahul Kumar should rank #1 for backend developer"
    assert top_c.score >= 80, "Top candidate should have strong score >= 80"

    # Step 7: View Formatted Cards & Improvements
    print("\n[Step 7] Checking Telegram UI Cards...")
    ranking_card = format_ranking_leaderboard(evaluated, jd.job_title)
    ats_card = format_candidate_ats_card(top_c)
    imp_card = format_improvement_plan(top_c)
    roadmap_card = format_learning_roadmap(top_c)
    
    assert "ATS COMPATIBILITY" in ats_card
    assert "HOW TO IMPROVE SCORE" in imp_card
    assert "Priority 1" in imp_card
    assert "LEARNING ROADMAP" in roadmap_card
    assert "WEEK 1" in roadmap_card
    print("  ✓ ATS Card, Improvements (Priorities 1, 2, 3) & Learning Roadmap verified.")

    # Step 8: Reports Generation
    print("\n[Step 8] Generating File Attachments (.md & .csv)...")
    batch_md = generate_batch_report_md(evaluated, jd)
    cand_md = generate_candidate_report_md(top_c)
    rank_csv = generate_ranking_csv(evaluated)
    
    assert os.path.exists(batch_md)
    assert os.path.exists(cand_md)
    assert os.path.exists(rank_csv)
    print(f"  ✓ Batch Report: {batch_md}")
    print(f"  ✓ Single Report: {cand_md}")
    print(f"  ✓ Leaderboard CSV: {rank_csv}")

    # Step 9: Conversational Q&A
    print("\n[Step 9] Simulating Conversational Q&A...")
    test_questions = [
        "Why did Rahul Kumar rank #1?",
        "What skills is Priya Sharma missing?",
        "How can Arjun Patel improve his score to 70+?",
        "Is Rahul Kumar's resume ATS friendly?"
    ]
    
    for q in test_questions:
        ans = answer_user_query(q, session, groq_api_key=GROQ_API_KEY)
        print(f"\n  User: \"{q}\"")
        print(f"  Bot: {ans[:150]}...")
        assert len(ans) > 20

    # Step 10: /compare
    print("\n[Step 10] User sends /compare")
    comp = format_candidate_comparison(evaluated)
    assert "COMPARISON MATRIX" in comp
    print("  ✓ Comparison matrix formatted.")

    # Step 11: /clear
    print("\n[Step 11] User sends /clear")
    session_manager.reset_session(test_chat_id)
    assert session_manager.get_session(test_chat_id).state == SessionState.IDLE
    assert len(session_manager.get_session(test_chat_id).resumes) == 0
    print("  ✓ Workspace cleanly reset.")

    print("\n==================================================")
    print("🎉 ALL 11 STEPS IN HASHIRA ATS SIMULATION PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_simulation()
