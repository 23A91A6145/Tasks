"""
Hashira ATS - Comprehensive Markdown and CSV Report Generator
Generates full multi-section ATS reports and candidate ranking files for Telegram delivery.
"""
import os
import csv
import re
from typing import List
from models import CandidateResult, JDAnalysis
from config import REPORTS_DIR

def generate_candidate_report_md(result: CandidateResult, output_dir: str = str(REPORTS_DIR)) -> str:
    """Generate 14-section single candidate markdown report."""
    os.makedirs(output_dir, exist_ok=True)
    safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', result.candidate_name.lower())
    filepath = os.path.join(output_dir, f"hashira_ats_{safe_name}_report.md")
    
    bd = result.score_breakdown
    
    lines = [
        f"# 🤖 HASHIRA ATS — CANDIDATE INTELLIGENCE REPORT",
        f"",
        f"---",
        f"",
        f"## 1. Candidate Overview",
        f"- **Candidate Name:** {result.candidate_name}",
        f"- **Source File:** `{result.filename}`",
        f"- **ATS Verification Date:** Current Session",
        f"",
        f"## 2. Target Job",
        f"- **Target Position:** {result.target_role}",
        f"",
        f"## 3. Overall ATS Compatibility Score",
        f"### **{result.score} / 100** — {result.compatibility_band}",
        f"*Note: This is a Hashira ATS Compatibility Score based on transparent weighted rubric.*",
        f"",
        f"## 4. Transparent Score Breakdown",
        f"| Dimension | Weight | Score | Coverage |",
        f"| :--- | :---: | :---: | :---: |",
        f"| Required Skill Coverage | 30% | {bd.required_skills}/30 | {int((bd.required_skills/30)*100)}% |",
        f"| Technical Skill Match | 20% | {bd.technical_skills}/20 | {int((bd.technical_skills/20)*100)}% |",
        f"| Semantic Relevance | 15% | {bd.semantic_relevance}/15 | {int((bd.semantic_relevance/15)*100)}% |",
        f"| Experience/Role Alignment | 10% | {bd.experience_match}/10 | {int((bd.experience_match/10)*100)}% |",
        f"| Keyword & Context Coverage | 10% | {bd.keyword_coverage}/10 | {int((bd.keyword_coverage/10)*100)}% |",
        f"| Projects & Achievement Evidence | 10% | {bd.projects_evidence}/10 | {int((bd.projects_evidence/10)*100)}% |",
        f"| ATS Format & Readability | 5% | {bd.ats_readability}/5 | {int((bd.ats_readability/5)*100)}% |",
        f"| **Total Score** | **100%** | **{result.score}/100** | **{result.compatibility_band}** |",
        f"",
        f"## 5. Matched Skills (✅)",
        ", ".join([f"`{s}`" for s in result.matched_skills]) if result.matched_skills else "*None verified with evidence*",
        f"",
        f"## 6. Partial / Preferred Skills (🟡)",
        ", ".join([f"`{s}`" for s in result.partial_skills]) if result.partial_skills else "*None detected*",
        f"",
        f"## 7. Missing Skills (❌)",
        ", ".join([f"`{s}`" for s in result.missing_skills]) if result.missing_skills else "*No critical skills missing*",
        f"",
        f"## 8. Verified Strengths & Weaknesses",
        f"### Strengths",
    ]
    for s in result.strengths:
        lines.append(f"- {s}")
    lines.extend([
        f"",
        f"### Weaknesses & Gaps",
    ])
    for w in result.weaknesses:
        lines.append(f"- {w}")
        
    lines.extend([
        f"",
        f"## 9. 🚀 Actionable Improvement Plan",
        f"Target Score: **90+/100**"
    ])
    for imp in result.structured_improvements:
        lines.extend([
            f"",
            f"### Priority {imp.priority} {imp.level} {imp.skill}",
            f"- **Why:** {imp.why}",
            f"- **Action:** {imp.action}",
            f"- **Expected Potential Gain:** {imp.expected_improvement}"
        ])

    lines.extend([
        f"",
        f"## 10. 📚 Structured Learning Roadmap",
    ])
    for week in result.structured_roadmap:
        lines.extend([
            f"",
            f"### WEEK {week.week_number}: {week.title}",
            f"```text",
            f"{week.title}",
        ])
        for idx, sub in enumerate(week.subtopics):
            branch = "└── " if idx == len(week.subtopics) - 1 else "├── "
            lines.append(f"{branch}{sub}")
        lines.append("```")

    lines.extend([
        f"",
        f"## 11. 💡 Recommended Projects to Build",
    ])
    for proj in result.recommended_projects:
        lines.append(f"- **{proj}**")

    lines.extend([
        f"",
        f"## 12. 🎓 Recommended High-Quality Free Courses & Docs",
        f"| Skill | Recommended Resource | Source |",
        f"| :--- | :--- | :--- |",
    ])
    for res in result.free_resources:
        lines.append(f"| {res['skill']} | [{res['title']}]({res['url']}) | {res['provider']} |")

    lines.extend([
        f"",
        f"## 13. ATS Readability & Formatting Issues",
    ])
    if result.ats_formatting_issues:
        for issue in result.ats_formatting_issues:
            lines.append(f"- ⚠️ {issue}")
    else:
        lines.append("- ✅ No structural or contact issues found. Layout is ATS-compatible.")

    lines.extend([
        f"",
        f"## 14. 📝 Final Conclusion & Readiness Verdict",
        f"> {result.final_verdict}",
        f"",
        f"---",
        f"*Generated automatically by Hashira ATS — Resume Intelligence Engine.*"
    ])

    content = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return os.path.abspath(filepath)

def generate_batch_report_md(candidates: List[CandidateResult], jd: JDAnalysis, output_dir: str = str(REPORTS_DIR)) -> str:
    """Generate comprehensive multi-candidate ranking & intelligence report."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "hashira_ats_report.md")
    
    sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    total = len(sorted_candidates)
    avg_score = round(sum(c.score for c in sorted_candidates) / total, 1) if total else 0
    
    medals = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    lines = [
        f"# 🏆 HASHIRA ATS — BATCH CANDIDATE RANKING & INTELLIGENCE REPORT",
        f"",
        f"**Target Role:** {jd.job_title}  ",
        f"**Total Candidates Evaluated:** {total}  ",
        f"**Average Compatibility Score:** {avg_score} / 100  ",
        f"**Top Ranked Candidate:** {sorted_candidates[0].candidate_name} ({sorted_candidates[0].score}/100)  ",
        f"",
        f"---",
        f"",
        f"## 🏆 Candidate Leaderboard",
        f"",
        f"| Rank | Candidate | Score | Compatibility Band | Matched Skills | Key Gaps |",
        f"| :---: | :--- | :---: | :---: | :--- | :--- |",
    ]
    
    for idx, c in enumerate(sorted_candidates):
        rank_icon = medals[idx] if idx < len(medals) else f"#{idx+1}"
        matched_str = ", ".join(c.matched_skills[:4]) or "None"
        gaps_str = ", ".join(c.missing_skills[:3]) or "None"
        lines.append(f"| {rank_icon} | **{c.candidate_name}** | **{c.score}/100** | {c.compatibility_band} | {matched_str} | {gaps_str} |")
        
    lines.extend([
        f"",
        f"---",
        f"",
        f"## 📊 Comparative Analysis & Score Breakdown",
        f"",
        f"| Candidate | Required (30) | Tech (20) | Semantic (15) | Exp (10) | Keywords (10) | Evidence (10) | ATS (5) | Total (100) |",
        f"| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ])
    
    for c in sorted_candidates:
        b = c.score_breakdown
        lines.append(f"| **{c.candidate_name}** | {b.required_skills} | {b.technical_skills} | {b.semantic_relevance} | {b.experience_match} | {b.keyword_coverage} | {b.projects_evidence} | {b.ats_readability} | **{c.score}** |")

    lines.extend([
        f"",
        f"---",
        f"",
        f"## 👤 Individual Candidate Detailed Breakdowns",
        f""
    ])
    
    for idx, c in enumerate(sorted_candidates):
        rank_icon = medals[idx] if idx < len(medals) else f"#{idx+1}"
        lines.extend([
            f"### {rank_icon} {c.candidate_name} — {c.score}/100 ({c.compatibility_band})",
            f"- **Source File:** `{c.filename}`",
            f"- **Matched Skills:** {', '.join(c.matched_skills) if c.matched_skills else 'None'}",
            f"- **Missing Skills:** {', '.join(c.missing_skills) if c.missing_skills else 'None'}",
            f"- **Verdict:** {c.final_verdict}",
            f""
        ])
        
    lines.extend([
        f"---",
        f"*Generated by Hashira ATS Intelligence System.*"
    ])
    
    content = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return os.path.abspath(filepath)

def generate_ranking_csv(candidates: List[CandidateResult], output_dir: str = str(REPORTS_DIR)) -> str:
    """Generate CSV summary of candidate rankings."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "candidate_ranking.csv")
    
    sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Rank", "Candidate Name", "Filename", "Score", "Band",
            "Required Skills (30)", "Tech Match (20)", "Semantic (15)",
            "Experience (10)", "Keywords (10)", "Projects (10)", "ATS Readability (5)",
            "Matched Skills", "Missing Skills", "Verdict"
        ])
        for idx, c in enumerate(sorted_candidates):
            b = c.score_breakdown
            writer.writerow([
                idx + 1, c.candidate_name, c.filename, c.score, c.compatibility_band,
                b.required_skills, b.technical_skills, b.semantic_relevance,
                b.experience_match, b.keyword_coverage, b.projects_evidence, b.ats_readability,
                "; ".join(c.matched_skills), "; ".join(c.missing_skills), c.final_verdict
            ])
            
    return os.path.abspath(filepath)
