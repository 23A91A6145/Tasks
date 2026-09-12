"""
Hashira ATS - Telegram UI Views & Message Templates
Renders user-friendly, structured Telegram cards, score breakdowns, roadmaps, and rankings.
"""
from typing import List
from models import CandidateResult, JDAnalysis

def format_welcome_message() -> str:
    return """🤖 <b>HASHIRA ATS</b>

<b>AI-Powered Resume Intelligence</b>

I analyze resumes against Job Descriptions and provide:

🎯 ATS Compatibility Score
🧠 Skill Matching
❌ Missing Skills
⚠️ Partial Skills
📊 Candidate Ranking
🚀 Improvement Plan
📚 Learning Roadmap
🎓 Recommended Courses
💡 Projects to Build
📝 Final Conclusion

<b>Commands:</b>
/new — Start new ATS analysis
/status — Check current workspace
/analyze — Run ATS evaluation
/report — Download full intelligence report
/compare — Side-by-side comparison
/clear — Reset workspace
/help — Show commands & help"""

def format_new_analysis_prompt() -> str:
    return """🆕 <b>New ATS Analysis</b>

<b>Step 1/2:</b> Please upload the Job Description.

<b>Supported formats:</b>
• PDF
• DOCX
• TXT

<i>You can also paste the Job Description directly as a text message.</i>"""

def format_jd_received(jd: JDAnalysis) -> str:
    req_list = "\n".join([f"• {s.title()}" for s in jd.mandatory_skills[:8]]) or "• General software engineering requirements"
    pref_list = ", ".join([s.title() for s in jd.preferred_skills[:6]]) if jd.preferred_skills else "None specified"
    
    return f"""✅ <b>Job Description received.</b>

📌 <b>Role detected:</b>
<b>{jd.job_title}</b>

🔎 <b>Initial requirements:</b>
{req_list}

✨ <b>Preferred:</b> {pref_list}

<b>Step 2/2:</b> Now upload one or more resumes (PDF, DOCX, TXT)."""

def format_resume_received(count: int, filename: str, candidate_name: str, target_role: str) -> str:
    medals = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    icon = medals[count - 1] if count <= len(medals) else f"{count}️⃣"
    
    return f"""✅ <b>Resume received</b>
{icon} <b>{filename}</b> ({candidate_name})

📊 <b>Current workspace</b>
• <b>JD:</b> {target_role}
• <b>Resumes uploaded:</b> {count}

Send /analyze when ready, or continue uploading more resumes!"""

def format_workspace_status(role: str, resume_count: int, resumes_info: List[str], is_analyzed: bool) -> str:
    res_list = "\n".join([f"  {idx+1}. {r}" for idx, r in enumerate(resumes_info)]) if resumes_info else "  None uploaded yet"
    status_text = "Completed (Q&A ready)" if is_analyzed else ("Ready for /analyze" if resume_count > 0 else "Waiting for resumes")
    
    return f"""📊 <b>Current Workspace Status</b>
━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>Job Description:</b> {role if role else "Not loaded (Send /new)"}
👥 <b>Resumes ({resume_count}):</b>
{res_list}

⚡ <b>Analysis Status:</b> {status_text}
━━━━━━━━━━━━━━━━━━━━━━"""

def format_candidate_ats_card(result: CandidateResult) -> str:
    """Format single candidate ATS Compatibility score card."""
    bd = result.score_breakdown
    
    # Compatibility emoji
    if result.score >= 80:
        band_emoji = "🟢"
    elif result.score >= 65:
        band_emoji = "🟡"
    else:
        band_emoji = "🔴"
        
    matched_str = "\n".join([f"• {s}" for s in result.matched_skills[:8]]) or "• None verified"
    partial_str = "\n".join([f"• {s}" for s in result.partial_skills[:5]]) or "• None"
    missing_str = "\n".join([f"• {s}" for s in result.missing_skills[:8]]) or "• None"

    return f"""🎯 <b>ATS COMPATIBILITY</b>

<b>Candidate:</b> {result.candidate_name}
<b>Role:</b> {result.target_role}

━━━━━━━━━━━━━━━━━━━━━━
<b>Overall Score:</b> <b>{result.score} / 100</b>
{band_emoji} <b>{result.compatibility_band}</b>
<i>(Hashira ATS Compatibility Score)</i>
━━━━━━━━━━━━━━━━━━━━━━

📈 <b>Score Breakdown:</b>
Required Skills:      <b>{bd.required_skills}/30</b>
Technical Match:      <b>{bd.technical_skills}/20</b>
Semantic Match:       <b>{bd.semantic_relevance}/15</b>
Experience:           <b>{bd.experience_match}/10</b>
Keywords:             <b>{bd.keyword_coverage}/10</b>
Evidence:             <b>{bd.projects_evidence}/10</b>
ATS Format:           <b>{bd.ats_readability}/5</b>

━━━━━━━━━━━━━━━━━━━━━━
✅ <b>MATCHED SKILLS:</b>
{matched_str}

🟡 <b>PARTIAL SKILLS:</b>
{partial_str}

❌ <b>MISSING SKILLS:</b>
{missing_str}"""

def format_improvement_plan(result: CandidateResult) -> str:
    """Format the 3-tier actionable improvement plan."""
    lines = [
        f"🚀 <b>HOW TO IMPROVE SCORE</b>",
        f"<b>Candidate:</b> {result.candidate_name}",
        f"Current: <b>{result.score}/100</b> | Target: <b>90+/100</b>",
        f"━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for imp in result.structured_improvements[:3]:
        lines.extend([
            f"<b>Priority {imp.priority} {imp.level}</b>",
            f"<b>{imp.skill}</b>",
            f"<b>Why:</b> {imp.why}",
            f"<b>Action:</b> {imp.action}",
            f""
        ])
        
    lines.append("<b>Expected potential improvement:</b> ~8–15 points depending on verified evidence.")
    return "\n".join(lines)

def format_learning_roadmap(result: CandidateResult) -> str:
    """Format tree-structure 4-week learning roadmap."""
    lines = [
        f"📚 <b>LEARNING ROADMAP</b>",
        f"<i>Tailored for {result.candidate_name} ({result.target_role})</i>",
        f"━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for week in result.structured_roadmap[:4]:
        lines.append(f"<b>WEEK {week.week_number}</b>\n<code>{week.title}</code>")
        tree_lines = []
        for idx, sub in enumerate(week.subtopics[:4]):
            branch = "└── " if idx == len(week.subtopics[:4]) - 1 else "├── "
            tree_lines.append(f"{branch}{sub}")
        lines.append("<pre>" + "\n".join(tree_lines) + "</pre>\n")
        
    return "\n".join(lines)

def format_courses_and_conclusion(result: CandidateResult) -> str:
    """Format courses recommendations and final conclusion."""
    courses_lines = []
    for res in result.free_resources[:5]:
        courses_lines.append(f"• <b>{res['skill']}:</b> <a href='{res['url']}'>{res['title']}</a> (<i>{res['provider']}</i>)")
        
    courses_str = "\n".join(courses_lines) if courses_lines else "• Official documentation and interactive tutorials."
    
    return f"""🎓 <b>RECOMMENDED RESOURCES</b>
{courses_str}

━━━━━━━━━━━━━━━━━━━━━━
📝 <b>FINAL CONCLUSION</b>
{result.final_verdict}

💬 <i>You can ask any questions about this candidate or resume below!</i>"""

def format_ranking_leaderboard(candidates: List[CandidateResult], target_role: str) -> str:
    """Format multi-candidate leaderboard."""
    sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    total = len(candidates)
    avg = round(sum(c.score for c in candidates) / total, 1) if total else 0
    top = sorted_candidates[0]
    
    medals = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    lines = [
        f"🏆 <b>CANDIDATE RANKING</b>",
        f"🎯 <b>Role:</b> {target_role}",
        f"━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for idx, c in enumerate(sorted_candidates):
        icon = medals[idx] if idx < len(medals) else f"#{idx+1}"
        score_emoji = "🟢" if c.score >= 80 else ("🟡" if c.score >= 65 else "🔴")
        lines.extend([
            f"{icon} <b>{c.candidate_name}</b>",
            f"   ⭐ <b>{c.score}/100</b> {score_emoji} {c.compatibility_band}",
            f""
        ])
        
    lines.extend([
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 <b>Summary:</b>",
        f"• <b>Candidates Analyzed:</b> {total}",
        f"• <b>Top Candidate:</b> {top.candidate_name} ({top.score}/100)",
        f"• <b>Average Score:</b> {avg}/100",
        f"• <b>Common Skill Gap:</b> {top.missing_skills[0] if top.missing_skills else 'Cloud Deployment'}",
        f"",
        f"📎 <i>Full detailed report (.md) attached below.</i>",
        f"💬 <i>Ask follow-up questions anytime (e.g. 'Why is {top.candidate_name} #1?', 'Compare candidate 1 and 2')</i>"
    ])
    return "\n".join(lines)

def format_candidate_comparison(candidates: List[CandidateResult]) -> str:
    """Side-by-side comparative table."""
    if len(candidates) < 2:
        return "⚠️ You need at least 2 candidates in the workspace to compare."
        
    sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    
    lines = [
        f"⚖️ <b>CANDIDATE COMPARISON MATRIX</b>",
        f"━━━━━━━━━━━━━━━━━━━━━━"
    ]
    
    for idx, c in enumerate(sorted_candidates):
        bd = c.score_breakdown
        lines.extend([
            f"<b>#{idx+1} {c.candidate_name}</b> (<b>{c.score}/100</b> — {c.compatibility_band})",
            f"• Required Skills: {bd.required_skills}/30",
            f"• Technical Match: {bd.technical_skills}/20",
            f"• Matched: {', '.join(c.matched_skills[:4]) or 'None'}",
            f"• Missing: {', '.join(c.missing_skills[:3]) or 'None'}",
            f""
        ])
        
    return "\n".join(lines)
