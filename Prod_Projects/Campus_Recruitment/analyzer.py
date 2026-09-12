"""
Hashira ATS - Core Intelligence Orchestrator
Combines deterministic skill extraction, Groq AI semantic analysis,
and structured roadmap / improvement generation.
"""
import os
import json
import re
from typing import Dict, List, Tuple, Optional
from models import CandidateResult, ScoreBreakdown, JDAnalysis, ImprovementItem, RoadmapWeek
from scoring import (
    extract_skills_from_jd,
    compute_deterministic_score,
    evaluate_ats_readability,
    normalize_text
)
from prompts import (
    SYSTEM_PROMPT,
    ANALYSIS_SCHEMA_PROMPT,
    get_free_resources_for_skills,
    generate_weekly_roadmap,
    generate_structured_improvements
)
from parser import detect_candidate_name

def analyze_job_description(jd_text: str) -> JDAnalysis:
    """Extract job title, mandatory skills, preferred skills, and details from JD."""
    mandatory, preferred = extract_skills_from_jd(jd_text)
    
    # Extract Job Title from first 6 lines
    lines = [l.strip() for l in jd_text.split('\n') if l.strip()]
    title = "Backend Developer"
    for line in lines[:6]:
        clean_line = re.sub(r'^(?:job\s+title|role|position)\s*:\s*', '', line, flags=re.IGNORECASE).strip()
        if any(role in clean_line.lower() for role in ["developer", "engineer", "architect", "intern", "analyst", "lead", "specialist"]):
            title = clean_line[:60].strip()
            break
            
    return JDAnalysis(
        job_title=title,
        mandatory_skills=mandatory,
        preferred_skills=preferred,
        raw_text=jd_text
    )

def query_ai_semantic(
    resume_text: str,
    jd_text: str,
    mandatory_skills: List[str],
    matched_skills: List[str],
    missing_skills: List[str],
    api_key: Optional[str] = None
) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Call Groq API with JSON schema constraint for semantic depth.
    Returns: (result_dict, status_message)
    """
    if not api_key or not api_key.strip():
        return None, "No API key supplied; used deterministic engine."
        
    key = api_key.strip()
    user_message = f"""
JOB DESCRIPTION:
{jd_text[:3500]}

CANDIDATE RESUME:
{resume_text[:3500]}

PRE-PARSED SKILLS:
- Mandatory Skills in JD: {', '.join(mandatory_skills)}
- Deterministically Matched: {', '.join(matched_skills)}
- Deterministically Missing: {', '.join(missing_skills)}

CRITICAL INSTRUCTION:
Never infer that a candidate knows something merely because it is related to another skill. For instance, knowing Python + FastAPI does NOT mean they know Django.

{ANALYSIS_SCHEMA_PROMPT}
"""

    try:
        from groq import Groq
        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=2000,
            timeout=30.0
        )
        content = response.choices[0].message.content
        return json.loads(content), "Analyzed with Groq LLaMA-3.3-70B."
    except Exception as e:
        err_str = str(e)
        return None, f"Groq fallback: {err_str[:80]}"

def analyze_resume(
    resume_text: str,
    filename: str,
    jd: JDAnalysis,
    groq_api_key: Optional[str] = None
) -> CandidateResult:
    """
    Run full end-to-end ATS evaluation for a single candidate.
    """
    candidate_name = detect_candidate_name(resume_text, filename)
    
    # 1. Deterministic Scoring Baseline
    breakdown, skill_summary = compute_deterministic_score(
        resume_text=resume_text,
        jd_text=jd.raw_text,
        mandatory_skills=jd.mandatory_skills,
        preferred_skills=jd.preferred_skills
    )
    
    matched = skill_summary["matched"]
    missing = skill_summary["missing"]
    
    # 2. AI Semantic Refinement
    ai_data, ai_status = query_ai_semantic(
        resume_text=resume_text,
        jd_text=jd.raw_text,
        mandatory_skills=jd.mandatory_skills,
        matched_skills=matched,
        missing_skills=missing,
        api_key=groq_api_key
    )
    
    readability_score, formatting_issues = evaluate_ats_readability(resume_text)
    
    structured_improvements: List[ImprovementItem] = []
    structured_roadmap: List[RoadmapWeek] = []
    
    if ai_data:
        # Incorporate verified AI semantic score
        semantic_score = float(ai_data.get("semantic_score_15", breakdown.semantic_relevance))
        semantic_score = min(15.0, max(5.0, semantic_score))
        breakdown.semantic_relevance = round(semantic_score, 1)
        
        strengths = ai_data.get("strengths", [])
        weaknesses = ai_data.get("weaknesses", [])
        ai_missing = ai_data.get("missing_skills", [])
        partial_skills = ai_data.get("partial_skills", [])
        recommended_projects = ai_data.get("recommended_projects", [])
        final_verdict = ai_data.get("final_conclusion", "")
        
        # Parse structured improvements if present
        raw_imps = ai_data.get("improvements", [])
        for i, imp in enumerate(raw_imps):
            if isinstance(imp, dict):
                structured_improvements.append(ImprovementItem(
                    priority=int(imp.get("priority", i+1)),
                    level=str(imp.get("level", "🔴" if i < 2 else "🟡")),
                    skill=str(imp.get("skill", "Core Skill")),
                    why=str(imp.get("why", "Required by JD")),
                    action=str(imp.get("action", "Build project")),
                    expected_improvement=str(imp.get("expected_improvement", "~8–15 potential points"))
                ))
            elif isinstance(imp, str):
                structured_improvements.append(ImprovementItem(
                    priority=i+1,
                    level="🔴" if i < 2 else "🟡",
                    skill=missing[i] if i < len(missing) else "General Skill",
                    why="Identified gap in profile relative to requirements.",
                    action=imp,
                    expected_improvement="~5–10 potential points"
                ))
                
        # Parse structured roadmap weeks if present
        raw_weeks = ai_data.get("roadmap_weeks", [])
        for w in raw_weeks:
            if isinstance(w, dict) and "week_number" in w:
                structured_roadmap.append(RoadmapWeek(
                    week_number=int(w.get("week_number", 1)),
                    title=str(w.get("title", "Core Topic")),
                    subtopics=w.get("subtopics", [])
                ))

        combined_missing = sorted(list(set(missing + [s.lower() for s in ai_missing if isinstance(s, str)])))
    else:
        strengths = [
            f"Strong demonstrated skill in {', '.join([s.title() for s in matched[:4]])}." if matched else "Clear resume layout and educational foundation.",
            "Relevant experience matches core project goals.",
            "Solid alignment with primary programming stack."
        ]
        weaknesses = [
            f"No verified evidence found for {', '.join([s.title() for s in missing[:3]])}." if missing else "Could increase quantifiable engineering impact.",
            "Production deployment and metrics could be more explicit."
        ]
        partial_skills = [s.title() for s in jd.preferred_skills if s not in matched][:3]
        recommended_projects = [
            f"Build and containerize a backend service featuring {', '.join([s.title() for s in missing[:2]] or ['Redis', 'Docker'])} with full unit tests and API docs.",
            "Set up automated CI/CD deployment on cloud with monitoring and latency metrics."
        ]
        final_verdict = (
            f"Candidate shows solid compatibility for {jd.job_title} with proven competency in "
            f"{', '.join([s.title() for s in matched[:3]]) if matched else 'core computer science'}. "
            f"The primary areas for score growth are {', '.join([s.title() for s in missing[:2]]) or 'cloud and containerization'}. "
            f"Implementing the recommended improvements will meaningfully strengthen their hiring case."
        )
        combined_missing = missing

    # Fallback to structured templates if LLM didn't return them
    if not structured_improvements:
        structured_improvements = generate_structured_improvements(combined_missing, partial_skills)
    if not structured_roadmap:
        structured_roadmap = generate_weekly_roadmap(combined_missing, jd.job_title)

    # Flat string improvements for legacy compatibility
    flat_improvements = [f"{item.skill}: {item.action}" for item in structured_improvements]

    # Recompute total score
    total_score = round(
        breakdown.required_skills +
        breakdown.technical_skills +
        breakdown.semantic_relevance +
        breakdown.experience_match +
        breakdown.keyword_coverage +
        breakdown.projects_evidence +
        breakdown.ats_readability,
        0
    )
    total_score = int(min(100, max(15, total_score)))
    breakdown.total_score = total_score
    
    # Band determination
    if total_score >= 80:
        band = "STRONG MATCH"
    elif total_score >= 65:
        band = "GOOD MATCH"
    elif total_score >= 50:
        band = "MODERATE MATCH"
    else:
        band = "LOW MATCH"
        
    free_resources = get_free_resources_for_skills(combined_missing)
    
    return CandidateResult(
        candidate_name=candidate_name,
        filename=filename,
        target_role=jd.job_title,
        score=total_score,
        compatibility_band=band,
        score_breakdown=breakdown,
        matched_skills=[s.title() for s in matched],
        partial_skills=[s.title() for s in partial_skills],
        missing_skills=[s.title() for s in combined_missing],
        strengths=strengths,
        weaknesses=weaknesses,
        improvements=flat_improvements,
        structured_improvements=structured_improvements,
        recommended_projects=recommended_projects,
        learning_roadmap=[],
        structured_roadmap=structured_roadmap,
        free_resources=free_resources,
        ats_formatting_issues=formatting_issues,
        final_verdict=final_verdict,
        raw_text=resume_text
    )
