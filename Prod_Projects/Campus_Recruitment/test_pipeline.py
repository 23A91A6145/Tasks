"""
Hashira ATS - End-to-End Pipeline Verification Test
Verifies document parsing, deterministic ATS scoring, skill matching,
report generation, and Telegram formatting.
"""
import os
import sys
from parser import extract_text, detect_candidate_name
from analyzer import (
    analyze_job_description,
    analyze_resume,
    generate_markdown_report
)
from telegram_bot import (
    format_telegram_candidate_message,
    format_telegram_batch_message
)

def run_tests():
    print("==================================================")
    print("🚀 Starting Hashira ATS End-to-End Verification")
    print("==================================================")

    # 1. Test JD Parsing
    jd_path = "sample_data/sample_jd.txt"
    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    print(f"\n[Test 1] Parsing Job Description from {jd_path}...")
    jd = analyze_job_description(jd_text)
    print(f"  ✓ Job Title Detected: '{jd.job_title}'")
    print(f"  ✓ Mandatory Skills Extracted: {jd.mandatory_skills}")
    print(f"  ✓ Preferred Skills Extracted: {jd.preferred_skills}")
    
    assert "python" in jd.mandatory_skills, "Python should be detected as mandatory"
    assert "fastapi" in jd.mandatory_skills, "FastAPI should be detected as mandatory"
    assert "docker" in jd.mandatory_skills or "docker" in jd.preferred_skills, "Docker should be detected"
    print("  --> PASS: JD Intelligence extraction accurate.")

    # 2. Test Resume Evaluations (Multi-Candidate Batch)
    test_resumes = [
        ("sample_data/sample_resume_rahul.txt", "Rahul Kumar", "STRONG MATCH"),
        ("sample_data/sample_resume_priya.txt", "Priya Sharma", "GOOD MATCH"),
        ("sample_data/sample_resume_arjun.txt", "Arjun Patel", "LOW MATCH")
    ]

    evaluated_candidates = []

    for rpath, expected_name, expected_band in test_resumes:
        print(f"\n[Test 2] Evaluating candidate resume: {rpath}...")
        with open(rpath, "r", encoding="utf-8") as f:
            rtext = f.read()
            
        result = analyze_resume(
            resume_text=rtext,
            filename=os.path.basename(rpath),
            jd=jd,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        evaluated_candidates.append(result)

        print(f"  ✓ Detected Name: {result.candidate_name}")
        print(f"  ✓ Score: {result.score} / 100 ({result.compatibility_band})")
        print(f"  ✓ Matched Skills ({len(result.matched_skills)}): {result.matched_skills}")
        print(f"  ✓ Missing Skills ({len(result.missing_skills)}): {result.missing_skills}")
        print(f"  ✓ 7-Day Roadmap items: {len(result.learning_roadmap)}")
        print(f"  ✓ Free Resources mapped: {len(result.free_resources)}")
        
        # Save report
        rep_path = generate_markdown_report(result)
        print(f"  ✓ Generated Markdown Report: {rep_path}")
        assert os.path.exists(rep_path), "Report file must exist on disk"
        
        # Verify specific expectations for Rahul (backend specialist)
        if expected_name == "Rahul Kumar":
            lower_matched = [s.lower() for s in result.matched_skills]
            assert "python" in lower_matched, "Rahul should match Python"
            assert "fastapi" in lower_matched, "Rahul should match FastAPI"
            assert "docker" in lower_matched, "Rahul should match Docker"
            assert result.score >= 75, f"Rahul score should be >= 75, got {result.score}"

    print("  --> PASS: All candidate evaluations and reports generated.")

    # 3. Test Telegram Message Formatting
    print("\n[Test 3] Testing Telegram Message Formatting...")
    # Candidate card
    card_text = format_telegram_candidate_message(evaluated_candidates[0])
    assert "HASHIRA ATS" in card_text, "Card must include branding"
    assert evaluated_candidates[0].candidate_name in card_text, "Card must include candidate name"
    print(f"  ✓ Candidate Telegram Card preview length: {len(card_text)} characters")

    # Batch Leaderboard
    batch_text = format_telegram_batch_message(evaluated_candidates, jd.job_title)
    assert "LEADERBOARD" in batch_text or "BATCH REPORT" in batch_text, "Batch must include leaderboard"
    print(f"  ✓ Batch Leaderboard preview length: {len(batch_text)} characters")
    print("  --> PASS: Telegram templates formatted properly.")

    # 4. Edge Case Handling
    print("\n[Test 4] Testing Resiliency Edge Cases...")
    empty_res = analyze_resume(
        resume_text="Hello world, I am testing empty resume with no skills.",
        filename="empty.txt",
        jd=jd,
        groq_api_key=None
    )
    assert empty_res.score < 50, "Empty resume should receive low score"
    print(f"  ✓ Empty resume gracefully handled with score: {empty_res.score}/100")
    print("  --> PASS: Resiliency verified.")

    print("\n==================================================")
    print("🎉 ALL HASHIRA ATS TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
