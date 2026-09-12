"""
Hashira ATS - Core Data Models & State Machine Definitions
Represents candidates, job descriptions, scoring breakdowns, session state, and reports.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional

class SessionState(str, Enum):
    IDLE = "IDLE"
    WAITING_FOR_JD = "WAITING_FOR_JD"
    JD_RECEIVED = "JD_RECEIVED"
    WAITING_FOR_RESUMES = "WAITING_FOR_RESUMES"
    RESUMES_RECEIVED = "RESUMES_RECEIVED"
    ANALYZING = "ANALYZING"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"

@dataclass
class ScoreBreakdown:
    required_skills: float = 0.0      # max 30
    technical_skills: float = 0.0     # max 20
    semantic_relevance: float = 0.0   # max 15
    experience_match: float = 0.0     # max 10
    keyword_coverage: float = 0.0     # max 10
    projects_evidence: float = 0.0    # max 10
    ats_readability: float = 0.0      # max 5
    total_score: float = 0.0          # max 100

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ImprovementItem:
    priority: int                     # 1, 2, 3
    level: str                        # "🔴" or "🟡"
    skill: str
    why: str
    action: str
    expected_improvement: str = "~5–12 potential points"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RoadmapWeek:
    week_number: int
    title: str
    subtopics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class CandidateResult:
    candidate_name: str
    filename: str
    target_role: str
    score: int
    compatibility_band: str
    score_breakdown: ScoreBreakdown
    matched_skills: List[str] = field(default_factory=list)
    partial_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    structured_improvements: List[ImprovementItem] = field(default_factory=list)
    recommended_projects: List[str] = field(default_factory=list)
    learning_roadmap: List[Dict[str, str]] = field(default_factory=list)
    structured_roadmap: List[RoadmapWeek] = field(default_factory=list)
    free_resources: List[Dict[str, str]] = field(default_factory=list)
    ats_formatting_issues: List[str] = field(default_factory=list)
    final_verdict: str = ""
    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("raw_text", None)
        return d

@dataclass
class JDAnalysis:
    job_title: str
    mandatory_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    experience_level: str = "0-2 years"
    education: List[str] = field(default_factory=list)
    key_responsibilities: List[str] = field(default_factory=list)
    raw_text: str = ""

@dataclass
class UploadedResume:
    filename: str
    candidate_name: str
    raw_text: str
    doc_id: str = ""

@dataclass
class UserSession:
    chat_id: int
    state: SessionState = SessionState.IDLE
    current_jd: Optional[JDAnalysis] = None
    jd_raw_text: str = ""
    jd_filename: str = ""
    resumes: List[UploadedResume] = field(default_factory=list)
    analysis_results: List[CandidateResult] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    active_candidate_idx: Optional[int] = None

    def reset(self):
        self.state = SessionState.IDLE
        self.current_jd = None
        self.jd_raw_text = ""
        self.jd_filename = ""
        self.resumes.clear()
        self.analysis_results.clear()
        self.conversation_history.clear()
        self.active_candidate_idx = None
