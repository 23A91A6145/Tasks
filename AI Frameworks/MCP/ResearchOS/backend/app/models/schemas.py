from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.core.constants import ResearchMode, RunStatus, SourceType, VerificationStatus

class ResearchCreateRequest(BaseModel):
    query: str = Field(..., min_length=5, description="The research inquiry or topic")
    mode: ResearchMode = Field(default=ResearchMode.DEEP, description="Research mode / depth")
    include_academic: bool = Field(default=True, description="Query arXiv, OpenAlex, Semantic Scholar")
    include_web: bool = Field(default=True, description="Query Tavily / Brave / Web search")
    max_sources: int = Field(default=20, ge=3, le=50, description="Upper bound on sources to collect")

class SubQuestion(BaseModel):
    id: str
    question: str
    rationale: str
    search_queries: List[str]
    target_sources: List[SourceType] = [SourceType.ACADEMIC, SourceType.WEB]

class ResearchPlan(BaseModel):
    topic: str
    objective: str
    sub_questions: List[SubQuestion]
    planned_searches: int
    estimated_time_seconds: int

class SourceDocument(BaseModel):
    id: str
    title: str
    url: str
    source_type: SourceType
    author: Optional[str] = "Unknown"
    published_date: Optional[str] = None
    domain: str
    snippet: str
    full_text: Optional[str] = None
    reliability_score: float = 1.0

class EvidenceChunk(BaseModel):
    id: str
    source_id: str
    content: str
    chunk_index: int
    score: float = 0.0

class AtomicClaim(BaseModel):
    id: str
    claim_text: str
    confidence_score: float = 0.85
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    source_id: str
    evidence_snippet: str

class CitationRecord(BaseModel):
    index: int
    claim_id: str
    source_id: str
    source_title: str
    source_url: str
    quoted_passage: str
    relevance_score: float = 0.90
    factual_support_score: float = 0.92
    link_valid: bool = True

class ReportSection(BaseModel):
    title: str
    content: str

class FinalReport(BaseModel):
    title: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    mode: ResearchMode
    executive_summary: str
    sections: List[ReportSection]
    comparative_matrix: Optional[List[Dict[str, Any]]] = None
    recommendations: List[str]
    citations: List[CitationRecord]
    confidence_score: float
    markdown_content: str

class CriticFeedback(BaseModel):
    score: int
    coverage_score: int
    factuality_score: int
    citation_density_score: int
    passes_audit: bool
    critique_notes: List[str]
    replan_needed: bool
    suggested_queries: List[str] = []

class TraceStep(BaseModel):
    step_name: str
    status: str
    started_at: datetime
    duration_ms: int
    details: Dict[str, Any] = {}

class RunTrace(BaseModel):
    run_id: str
    steps: List[TraceStep]
    total_duration_ms: int
    total_sources: int
    total_claims: int
    total_citations: int

class ResearchRunResponse(BaseModel):
    id: str
    query: str
    mode: ResearchMode
    status: RunStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    plan: Optional[ResearchPlan] = None
    sources_count: int = 0
    claims_count: int = 0
    citations_count: int = 0
    critic_score: Optional[int] = None
    report: Optional[FinalReport] = None
    trace: Optional[RunTrace] = None

class EvaluationMetrics(BaseModel):
    faithfulness_score: float
    citation_validity_score: float
    context_precision_score: float
    source_diversity_score: float
    hallucination_index: float
    overall_quality_score: float
    assessment: str
