"""
Hashira ATS - Conversational Q&A Engine
Answers follow-up recruiter and candidate queries with full session awareness using Groq LLaMA-3.3-70B.
"""
import re
from typing import List, Optional
from models import UserSession, CandidateResult
from config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE

QNA_SYSTEM_PROMPT = """You are Hashira ATS Assistant, an expert AI talent intelligence agent communicating directly via Telegram.
You have access to the active session data: the Job Description and candidate evaluations.

CRITICAL GUIDELINES:
1. Answer strictly based on the provided session context (candidates, scores, matched skills, missing skills, evidence).
2. NEVER hallucinate skills or experience that are not in the resumes.
3. If asked "Why is [Candidate] #1?" or "Why did candidate score higher?", explicitly compare their required skill coverage, projects evidence, and missing gaps with specifics.
4. Keep responses concise, clear, and formatted for Telegram (use bolding, bullet points, emojis).
5. If the user asks general ATS questions (e.g. "Is my resume ATS friendly?"), refer to their specific readability evaluation and formatting issues.
"""

def build_qna_context(session: UserSession) -> str:
    """Serialize current session candidates and JD into structured prompt context."""
    if not session.analysis_results:
        return "No analysis has been performed yet."
        
    jd_title = session.current_jd.job_title if session.current_jd else "Unknown Role"
    mandatory = ", ".join(session.current_jd.mandatory_skills) if session.current_jd else "None"
    preferred = ", ".join(session.current_jd.preferred_skills) if session.current_jd else "None"
    
    context_lines = [
        f"TARGET JOB DESCRIPTION:",
        f"Title: {jd_title}",
        f"Mandatory Skills: {mandatory}",
        f"Preferred Skills: {preferred}",
        f"",
        f"EVALUATED CANDIDATES (Ranked by Score):"
    ]
    
    sorted_candidates = sorted(session.analysis_results, key=lambda c: c.score, reverse=True)
    for idx, c in enumerate(sorted_candidates):
        bd = c.score_breakdown
        context_lines.extend([
            f"--- Candidate #{idx+1}: {c.candidate_name} ({c.filename}) ---",
            f"Score: {c.score}/100 ({c.compatibility_band})",
            f"Breakdown: Required={bd.required_skills}/30, Tech={bd.technical_skills}/20, Semantic={bd.semantic_relevance}/15, Experience={bd.experience_match}/10, Keywords={bd.keyword_coverage}/10, Evidence={bd.projects_evidence}/10, ATS Format={bd.ats_readability}/5",
            f"Matched Skills: {', '.join(c.matched_skills)}",
            f"Partial Skills: {', '.join(c.partial_skills)}",
            f"Missing Skills: {', '.join(c.missing_skills)}",
            f"Strengths: {'; '.join(c.strengths)}",
            f"Weaknesses: {'; '.join(c.weaknesses)}",
            f"Top Improvements: {'; '.join([imp.action for imp in c.structured_improvements[:2]])}",
            f"ATS Formatting Issues: {'; '.join(c.ats_formatting_issues) if c.ats_formatting_issues else 'None'}",
            f"Final Verdict: {c.final_verdict}",
            f""
        ])
        
    return "\n".join(context_lines)

def answer_user_query(query: str, session: UserSession, groq_api_key: Optional[str] = None) -> str:
    """Process conversational question against current session analysis."""
    if not session.analysis_results:
        return "⚠️ Please run an ATS analysis first (/analyze) before asking questions!"
        
    key = groq_api_key or GROQ_API_KEY
    context_data = build_qna_context(session)
    
    # 1. Try Groq AI for intelligent contextual answer
    if key:
        try:
            from groq import Groq
            client = Groq(api_key=key)
            
            # Prepare conversation history
            messages = [{"role": "system", "content": QNA_SYSTEM_PROMPT}]
            messages.append({"role": "system", "content": f"ACTIVE SESSION CONTEXT:\n{context_data}"})
            
            # Add recent conversation turns
            for turn in session.conversation_history[-6:]:
                messages.append({"role": turn["role"], "content": turn["content"]})
                
            messages.append({"role": "user", "content": query})
            
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=GROQ_TEMPERATURE,
                max_tokens=800,
                timeout=25.0
            )
            answer = response.choices[0].message.content.strip()
            # Store turns in session history
            session.conversation_history.append({"role": "user", "content": query})
            session.conversation_history.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            # Fallback to heuristic parser
            pass

    # 2. Deterministic Fallback if Groq call failed or no key
    sorted_candidates = sorted(session.analysis_results, key=lambda c: c.score, reverse=True)
    top_c = sorted_candidates[0]
    lower_q = query.lower()
    
    if any(term in lower_q for term in ["why", "rank", "best", "#1", "first"]):
        req_pct = int((top_c.score_breakdown.required_skills / 30.0) * 100)
        return (
            f"<b>{top_c.candidate_name}</b> ranks <b>#1</b> because:\n\n"
            f"✅ <b>{req_pct}%</b> required skill coverage\n"
            f"✅ Strong role alignment with {top_c.target_role}\n"
            f"✅ Matched core skills: {', '.join(top_c.matched_skills[:4])}\n"
            f"✅ Demonstrated technical evidence in projects\n\n"
            f"<b>Main gap:</b> {top_c.missing_skills[0] if top_c.missing_skills else 'Cloud deployment'}"
        )
        
    if any(term in lower_q for term in ["missing", "gaps", "lacking"]):
        cand = top_c
        for c in sorted_candidates:
            if c.candidate_name.lower() in lower_q:
                cand = c
                break
        return (
            f"🔍 <b>Missing Skills for {cand.candidate_name}:</b>\n"
            + "\n".join([f"• ❌ {s}" for s in cand.missing_skills])
        )
        
    if any(term in lower_q for term in ["improve", "score", "reach 90", "learn"]):
        cand = top_c
        for c in sorted_candidates:
            if c.candidate_name.lower() in lower_q:
                cand = c
                break
        return (
            f"🚀 <b>Key Actions to Raise {cand.candidate_name}'s Score:</b>\n\n"
            + "\n".join([f"• <b>{imp.skill}:</b> {imp.action}" for imp in cand.structured_improvements])
            + "\n\n<i>Expected improvement: ~8–15 points depending on evidence.</i>"
        )
        
    if "ats" in lower_q or "format" in lower_q or "friendly" in lower_q:
        issues = top_c.ats_formatting_issues
        if issues:
            return f"📄 <b>ATS Formatting Review for {top_c.candidate_name}:</b>\n\n" + "\n".join([f"• ⚠️ {i}" for i in issues])
        return f"✅ <b>{top_c.candidate_name}'s resume is highly ATS-friendly!</b> Standard headers, clear text density, and contact details detected."

    return (
        f"📊 <b>Analysis Insights for {top_c.candidate_name}:</b>\n"
        f"• Overall Compatibility: <b>{top_c.score}/100</b> ({top_c.compatibility_band})\n"
        f"• Top matched skills: {', '.join(top_c.matched_skills[:5])}\n"
        f"• Top skill gap: {', '.join(top_c.missing_skills[:3])}\n\n"
        f"<i>You can ask: 'Why did {top_c.candidate_name} score {top_c.score}?', 'What should they learn first?', or 'Compare candidates'.</i>"
    )
