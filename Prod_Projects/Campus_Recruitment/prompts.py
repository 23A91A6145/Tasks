"""
Hashira ATS - Prompt Engineering, Curated Free Learning Resources & Roadmaps
Includes strict anti-hallucination guardrails and structured JSON schemas.
"""
from typing import Dict, List
from models import ImprovementItem, RoadmapWeek

SYSTEM_PROMPT = """You are a senior ATS Resume Evaluator and Talent Matching Specialist for Hashira ATS.
Your job is to objectively analyze candidate resumes against job descriptions with zero tolerance for hallucinations.

CRITICAL RULES:
1. NEVER INVENT or infer that a candidate knows something merely because it is related to another skill. For example, if a resume shows Python and FastAPI, but the JD requires Django, DO NOT assume or report that the candidate knows Django. Mark Django as MISSING.
2. Distinguish clearly between MANDATORY requirements and PREFERRED qualifications.
3. Be strictly evidence-backed: every matched skill must have clear evidence in the resume.
4. Provide structured, actionable, and encouraging feedback with estimated/potential score gains (never promise exact score increases).
5. Return ONLY a valid JSON object matching the exact schema requested without markdown formatting or code blocks.
"""

ANALYSIS_SCHEMA_PROMPT = """
Analyze the provided RESUME against the JOB DESCRIPTION.
Return a valid JSON object with the following keys:
{
  "semantic_score_15": float (6.0 to 15.0 indicating depth of contextual & semantic match),
  "strengths": ["list of 3-5 verified candidate strengths with direct evidence from resume"],
  "weaknesses": ["list of 2-4 verified candidate weaknesses or gaps relative to JD"],
  "missing_skills": ["list of explicit skills in JD not evidenced anywhere in resume"],
  "partial_skills": ["skills candidate touches on briefly but lacks deep evidence or production usage"],
  "improvements": [
    {
      "priority": 1,
      "level": "🔴",
      "skill": "Skill name",
      "why": "Specific reason why this hurts the score",
      "action": "Concrete hands-on project or deployment action to take",
      "expected_improvement": "~8–15 potential points"
    }
  ],
  "recommended_projects": ["2-3 practical portfolio projects to close identified skill gaps"],
  "roadmap_weeks": [
    {
      "week_number": 1,
      "title": "Topic/Skill Name",
      "subtopics": ["Concept 1", "Concept 2", "Concept 3", "Concept 4"]
    }
  ],
  "final_conclusion": "A professional 3-4 sentence verdict on candidate's hiring readiness, core match, and top action."
}
"""

FREE_LEARNING_CATALOG = {
    "redis": {
        "title": "Redis University - RU101: Introduction to Redis Data Structures",
        "url": "https://university.redis.com/courses/ru101/",
        "provider": "Redis Official"
    },
    "docker": {
        "title": "Docker Getting Started & Containerization Essentials",
        "url": "https://docs.docker.com/get-started/",
        "provider": "Docker Official"
    },
    "kubernetes": {
        "title": "Kubernetes Interactive Basics & Architecture",
        "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
        "provider": "CNCF Kubernetes Official"
    },
    "aws": {
        "title": "AWS Skill Builder & Cloud Practitioner Essentials",
        "url": "https://explore.skillbuilder.aws/",
        "provider": "AWS Skill Builder"
    },
    "gcp": {
        "title": "Google Cloud Skills Boost - Core Infrastructure Fundamentals",
        "url": "https://www.cloudskillsboost.google/",
        "provider": "Google Cloud"
    },
    "fastapi": {
        "title": "FastAPI Official Interactive Tutorial",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "provider": "FastAPI Official"
    },
    "django": {
        "title": "Django Girls & Django Official Tutorial",
        "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
        "provider": "Django Software Foundation"
    },
    "postgresql": {
        "title": "PostgreSQL Tutorial for Developers & DBA Fundamentals",
        "url": "https://www.postgresqltutorial.com/",
        "provider": "PostgreSQL Tutorial"
    },
    "python": {
        "title": "Python 3 Official Documentation & Tutorial",
        "url": "https://docs.python.org/3/tutorial/",
        "provider": "Python Software Foundation"
    },
    "git": {
        "title": "GitHub Skills - First Week on GitHub & Git Immersion",
        "url": "https://skills.github.com/",
        "provider": "GitHub Skills"
    },
    "ci/cd": {
        "title": "GitHub Actions Fundamentals: CI/CD Pipeline Automation",
        "url": "https://docs.github.com/en/actions/learn-github-actions",
        "provider": "GitHub Documentation"
    },
    "rest api": {
        "title": "RESTful API Architectural Constraints & Best Practices",
        "url": "https://restfulapi.net/",
        "provider": "REST API Guide"
    },
    "kafka": {
        "title": "Apache Kafka Quickstart & Event Streaming Concepts",
        "url": "https://kafka.apache.org/quickstart",
        "provider": "Apache Software Foundation"
    },
    "microservices": {
        "title": "Microservice Architecture Patterns & Best Practices",
        "url": "https://microservices.io/",
        "provider": "Chris Richardson Microservices"
    }
}

DEFAULT_TOPICS = {
    "redis": ["Data structures", "Caching strategies", "TTL & eviction", "Pub/Sub"],
    "aws": ["EC2 & Compute", "S3 Storage", "IAM Policies", "Cloud Deployment"],
    "docker": ["Images & Containers", "Dockerfile optimization", "Multi-stage builds", "Docker Compose"],
    "kubernetes": ["Pods & Deployments", "Services & Ingress", "ConfigMaps & Secrets", "Cluster setup"],
    "ci/cd": ["Workflow triggers", "Automated unit tests", "Artifact deployment", "Production pipelines"],
    "django": ["Models & ORM", "Views & URLs", "Admin & Auth", "Django REST Framework"],
    "microservices": ["Service boundaries", "API Gateway", "Inter-service comms", "Distributed logging"],
    "kafka": ["Topics & Partitions", "Producers & Consumers", "Message offsets", "Stream processing"]
}

def get_free_resources_for_skills(missing_skills: List[str]) -> List[Dict[str, str]]:
    """Lookup curated free high-quality educational links strictly for identified missing skills."""
    resources = []
    seen = set()
    for skill in missing_skills:
        skill_key = skill.lower()
        if skill_key in FREE_LEARNING_CATALOG and skill_key not in seen:
            item = FREE_LEARNING_CATALOG[skill_key]
            resources.append({
                "skill": skill.title(),
                "title": item["title"],
                "url": item["url"],
                "provider": item["provider"]
            })
            seen.add(skill_key)

    # Fallback to general best-practices if none matched
    if not resources:
        resources.append({
            "skill": "Git & CI/CD",
            "title": "GitHub Skills Interactive Labs",
            "url": "https://skills.github.com/",
            "provider": "GitHub Skills"
        })
        resources.append({
            "skill": "System Design",
            "title": "System Design Primer by Donne Martin",
            "url": "https://github.com/donnemartin/system-design-primer",
            "provider": "Open Source Community"
        })
    return resources

def generate_weekly_roadmap(missing_skills: List[str], target_role: str) -> List[RoadmapWeek]:
    """Builds a 4-week tree roadmap matching user specification."""
    skills_to_cover = [s.lower() for s in missing_skills if s.lower() in DEFAULT_TOPICS]
    
    # Fill remaining from missing_skills or standard defaults
    for s in missing_skills:
        if s.lower() not in skills_to_cover:
            skills_to_cover.append(s.lower())
    
    defaults = ["redis", "aws", "docker", "production backend"]
    for d in defaults:
        if len(skills_to_cover) < 4:
            if d not in skills_to_cover:
                skills_to_cover.append(d)

    roadmap = []
    for week_num in range(1, 5):
        skill_name = skills_to_cover[week_num - 1]
        title = f"{skill_name.title()} Fundamentals" if skill_name != "production backend" else "Production Backend & Cloud"
        
        if skill_name in DEFAULT_TOPICS:
            subtopics = DEFAULT_TOPICS[skill_name]
        elif skill_name == "production backend":
            subtopics = ["Monitoring & Metrics", "Centralized Logging", "CI/CD Pipeline", "Autoscaling"]
        else:
            subtopics = [
                f"{skill_name.title()} Core Syntax & Setup",
                f"{skill_name.title()} Best Practices",
                f"Hands-on Integration Project",
                f"Testing & Production Checklist"
            ]
            
        roadmap.append(RoadmapWeek(
            week_number=week_num,
            title=title,
            subtopics=subtopics
        ))
    return roadmap

def generate_structured_improvements(missing_skills: List[str], partial_skills: List[str]) -> List[ImprovementItem]:
    """Generate structured priority items for the improvement engine."""
    items = []
    p = 1
    # Priority 1: Top missing mandatory skill
    if missing_skills:
        skill = missing_skills[0].title()
        items.append(ImprovementItem(
            priority=p,
            level="🔴",
            skill=skill,
            why="Required by Job Description but no demonstrated evidence found in resume.",
            action=f"Build and deploy a working backend service featuring {skill}.",
            expected_improvement="~8–15 potential points"
        ))
        p += 1
        
    # Priority 2: Second missing skill
    if len(missing_skills) > 1:
        skill = missing_skills[1].title()
        items.append(ImprovementItem(
            priority=p,
            level="🔴",
            skill=skill,
            why=f"Listed in core stack requirements; absence impacts technical matching score.",
            action=f"Add {skill} integration into an existing repository with benchmarked test cases.",
            expected_improvement="~6–10 potential points"
        ))
        p += 1
        
    # Priority 3: Partial or third missing skill
    if partial_skills:
        skill = partial_skills[0].title()
        items.append(ImprovementItem(
            priority=p,
            level="🟡",
            skill=skill,
            why="Mentioned briefly in resume but lacks production evidence or quantifiable outcome.",
            action=f"Deepen resume bullets for {skill} with architectural impact and latency metrics.",
            expected_improvement="~4–8 potential points"
        ))
    elif len(missing_skills) > 2:
        skill = missing_skills[2].title()
        items.append(ImprovementItem(
            priority=p,
            level="🟡",
            skill=skill,
            why="Preferred qualification that would differentiate your profile from peer candidates.",
            action=f"Containerize or automate deployment with {skill}.",
            expected_improvement="~3–6 potential points"
        ))
        
    return items
