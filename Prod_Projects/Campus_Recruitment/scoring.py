"""
Hashira ATS - Deterministic ATS & Heuristic Scoring Engine
Calculates explainable compatibility scores using normalized skill taxonomy,
keyword density, structural formatting checks, and weighted components.
"""
import re
from typing import Dict, List, Set, Tuple
from models import ScoreBreakdown

# Skill Normalization Map (canonical -> aliases)
SYNONYM_MAP = {
    "python": ["python", "python3", "py"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "django": ["django", "django rest framework", "drf"],
    "postgresql": ["postgresql", "postgres", "psql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "git": ["git", "github", "gitlab"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "github actions", "jenkins"],
    "rest api": ["rest api", "restful api", "rest", "restful apis"],
    "graphql": ["graphql"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs", "node"],
    "sql": ["sql", "rdbms", "relational database"],
    "nosql": ["nosql"],
    "linux": ["linux", "ubuntu", "unix", "bash", "shell scripting"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf"],
    "generative ai": ["generative ai", "genai", "llm", "large language models", "rag"],
    "data structures": ["data structures", "dsa", "algorithms"],
    "microservices": ["microservices", "distributed systems"],
    "kafka": ["kafka", "apache kafka"],
    "celery": ["celery", "task queue", "rabbitmq"]
}

# Reverse lookup for alias -> canonical
ALIAS_TO_CANONICAL = {}
for canonical, aliases in SYNONYM_MAP.items():
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical

COMMON_TECH_WORDS = set(ALIAS_TO_CANONICAL.keys())

def normalize_text(text: str) -> str:
    """Lowercase and clean string for regex search."""
    return text.lower()

def extract_matched_skills(text: str, candidate_skills: Set[str]) -> Set[str]:
    """Find which of the candidate skills appear in text (with word boundaries)."""
    normalized = normalize_text(text)
    matched = set()
    for skill in candidate_skills:
        # Check canonical and all aliases
        aliases = SYNONYM_MAP.get(skill, [skill])
        for alias in aliases:
            pattern = r'(?:\b|_)' + re.escape(alias) + r'(?:\b|_)'
            if re.search(pattern, normalized):
                matched.add(skill)
                break
    return matched

def extract_skills_from_jd(jd_text: str) -> Tuple[List[str], List[str]]:
    """
    Extract mandatory and preferred skills from JD using heuristic markers & taxonomy.
    """
    normalized = normalize_text(jd_text)
    
    # Heuristic split for mandatory vs preferred sections if present
    mandatory_found = set()
    preferred_found = set()
    
    lines = normalized.split('\n')
    current_section = "mandatory" # default
    
    for line in lines:
        if any(marker in line for marker in ["nice to have", "preferred", "plus", "good to have", "optional", "bonus"]):
            current_section = "preferred"
        elif any(marker in line for marker in ["required", "mandatory", "must have", "qualifications", "requirements", "core skills"]):
            current_section = "mandatory"
            
        for alias, canonical in ALIAS_TO_CANONICAL.items():
            pattern = r'(?:\b|_)' + re.escape(alias) + r'(?:\b|_)'
            if re.search(pattern, line):
                if current_section == "mandatory":
                    mandatory_found.add(canonical)
                else:
                    preferred_found.add(canonical)
                    
    # Preferred skills shouldn't duplicate mandatory
    preferred_found = preferred_found - mandatory_found
    
    # If no mandatory found, match across entire text
    if not mandatory_found:
        for alias, canonical in ALIAS_TO_CANONICAL.items():
            pattern = r'(?:\b|_)' + re.escape(alias) + r'(?:\b|_)'
            if re.search(pattern, normalized):
                mandatory_found.add(canonical)

    return sorted(list(mandatory_found)), sorted(list(preferred_found))

def evaluate_ats_readability(resume_text: str) -> Tuple[float, List[str]]:
    """
    Check standard ATS formatting compliance:
    - Section headings
    - Length / word count
    - Quantifiable metrics (numbers, %, etc.)
    - Contact email/phone presence
    """
    issues = []
    score = 5.0 # Max 5
    lower = resume_text.lower()
    
    # 1. Section headings check
    standard_sections = ["experience", "projects", "education", "skills"]
    missing_sections = [sec for sec in standard_sections if sec not in lower]
    if missing_sections:
        score -= min(2.0, len(missing_sections) * 0.5)
        issues.append(f"Missing recommended ATS sections: {', '.join(missing_sections).title()}")
        
    # 2. Contact check
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
    if not has_email:
        score -= 0.75
        issues.append("No valid email address detected in the header.")
    if not has_phone:
        score -= 0.5
        issues.append("No phone contact number detected in the header.")
        
    # 3. Quantifiable achievements (metrics, percentages, numbers)
    metric_matches = re.findall(r'\b\d+(?:\.\d+)?%|\b\d+x\b|\b\d+\s*(?:ms|k|m|users|requests|qps|sec|seconds)\b', lower)
    if len(metric_matches) < 2:
        score -= 0.75
        issues.append("Low quantifiable metrics: Consider adding measurable business outcomes (e.g. 'reduced latency by 35%').")

    # 4. Text density / word count
    words = resume_text.split()
    if len(words) < 150:
        score -= 1.0
        issues.append("Resume is very brief (<150 words); may lack sufficient depth for ATS indexers.")
    elif len(words) > 1500:
        score -= 0.5
        issues.append("Resume exceeds 1500 words; consider condensing to 1-2 focused pages.")

    return max(1.0, round(score, 1)), issues

def compute_deterministic_score(
    resume_text: str,
    jd_text: str,
    mandatory_skills: List[str],
    preferred_skills: List[str]
) -> Tuple[ScoreBreakdown, Dict[str, List[str]]]:
    """
    Computes deterministic ATS score components based on the official Hashira rubric:
    Component                         Weight
    Required skill coverage           30%
    Technical skill match             20%
    Semantic JD <-> Resume relevance  15% (heuristic baseline, refined by LLM)
    Experience/role alignment         10%
    Keyword/context coverage          10%
    Projects/achievement evidence     10%
    ATS readability                    5%
    --------------------------------------
    Total                            100%
    """
    all_jd_skills = set(mandatory_skills + preferred_skills)
    matched_all = extract_matched_skills(resume_text, all_jd_skills)
    
    matched_mandatory = [s for s in mandatory_skills if s in matched_all]
    missing_mandatory = [s for s in mandatory_skills if s not in matched_all]
    
    matched_preferred = [s for s in preferred_skills if s in matched_all]
    missing_preferred = [s for s in preferred_skills if s not in matched_all]
    
    # Equivalent skill clusters for smart matching (e.g. Postgres OR MySQL satisfies DB requirement)
    SKILL_EQUIVALENCE = [
        {"fastapi", "django", "flask"},
        {"postgresql", "mysql", "mongodb"},
        {"aws", "gcp", "azure"}
    ]

    # Calculate effective mandatory match with equivalence consideration
    effective_mandatory_total = len(mandatory_skills)
    effective_mandatory_matched = len(matched_mandatory)
    
    for cluster in SKILL_EQUIVALENCE:
        present_in_jd = cluster.intersection(set(mandatory_skills))
        if len(present_in_jd) > 1:
            # JD lists alternatives like (FastAPI or Django)
            if cluster.intersection(matched_all):
                # Candidate has at least one; adjust total denominator
                effective_mandatory_total -= (len(present_in_jd) - 1)

    effective_mandatory_total = max(1, effective_mandatory_total)
    req_ratio = min(1.0, effective_mandatory_matched / effective_mandatory_total)
    req_score = round(req_ratio * 30.0, 1)

    # 2. Technical skill match (max 20)
    # Give primary weight to mandatory match (15 max) and bonus to preferred (5 max)
    mandatory_ratio = min(1.0, len(matched_mandatory) / max(1, len(mandatory_skills)))
    preferred_ratio = min(1.0, len(matched_preferred) / max(1, len(preferred_skills))) if preferred_skills else 1.0
    tech_score = round((mandatory_ratio * 15.0) + (preferred_ratio * 5.0), 1)
    
    # 3. Semantic / Contextual overlap baseline (max 15)
    resume_tokens = set(re.findall(r'\b[a-z]{3,}\b', normalize_text(resume_text)))
    jd_tokens = set(re.findall(r'\b[a-z]{3,}\b', normalize_text(jd_text)))
    overlap = resume_tokens.intersection(jd_tokens)
    semantic_ratio = len(overlap) / max(len(jd_tokens), 1)
    # Jaccard/overlap scaling
    semantic_score = round(min(15.0, max(8.0, 8.0 + (semantic_ratio * 20.0))), 1)
    
    # 4. Experience & Role alignment (max 10)
    exp_matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?experience', normalize_text(resume_text))
    exp_score = 9.0 if exp_matches else 7.5
    
    # 5. Keyword / Context coverage (max 10)
    keyword_score = round(min(10.0, max(5.0, (req_ratio * 0.7 + semantic_ratio * 0.3) * 10.0)), 1)
    
    # 6. Projects & Achievement evidence (max 10)
    project_mentions = len(re.findall(r'\b(?:project|built|developed|implemented|architected|created)\b', normalize_text(resume_text)))
    project_score = min(10.0, round(6.0 + min(4.0, project_mentions * 0.8), 1))
    
    # 7. ATS readability (max 5)
    readability_score, issues = evaluate_ats_readability(resume_text)
    
    total = round(req_score + tech_score + semantic_score + exp_score + keyword_score + project_score + readability_score, 0)
    total = min(100.0, max(15.0, total))
    
    breakdown = ScoreBreakdown(
        required_skills=req_score,
        technical_skills=tech_score,
        semantic_relevance=semantic_score,
        experience_match=exp_score,
        keyword_coverage=keyword_score,
        projects_evidence=project_score,
        ats_readability=readability_score,
        total_score=total
    )
    
    skill_summary = {
        "matched": sorted(list(matched_mandatory + matched_preferred)),
        "missing": sorted(list(missing_mandatory + missing_preferred)),
        "mandatory_matched": sorted(matched_mandatory),
        "mandatory_missing": sorted(missing_mandatory),
        "preferred_matched": sorted(matched_preferred),
        "preferred_missing": sorted(missing_preferred)
    }
    
    return breakdown, skill_summary
