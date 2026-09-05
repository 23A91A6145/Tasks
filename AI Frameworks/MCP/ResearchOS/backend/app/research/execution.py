import uuid
from datetime import datetime, timezone
from typing import Optional, List
from backend.app.models.schemas import (
    ResearchCreateRequest, ResearchRunResponse, EvidenceChunk, SourceDocument
)
from backend.app.core.constants import RunStatus
from backend.app.agents.planner import PlannerAgent
from backend.app.agents.researcher import ResearcherAgent
from backend.app.agents.synthesizer import ResearchSynthesizer
from backend.app.agents.critic import ResearchCritic
from backend.app.retrieval.hybrid import HybridRRFRetriever
from backend.app.research.claims import ClaimExtractor
from backend.app.research.citations import CitationVerifier
from backend.app.observability.tracer import RunTracer
from backend.app.evaluation.metrics import ResearchEvaluator
from backend.app.core.logging import logger

class ResearchExecutionEngine:
    """
    Orchestrates the autonomous research pipeline:
    Plan -> Search -> Chunk/RRF -> Claim Extraction -> 4-Tier Citation -> Synthesis -> Critic -> Trace
    """

    @staticmethod
    async def execute_research(request: ResearchCreateRequest) -> ResearchRunResponse:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        tracer = RunTracer(run_id)
        created_at = datetime.now(timezone.utc)

        logger.info(f"Starting research run {run_id} for topic: '{request.query}'")

        # 1. Planning Phase
        tracer.start_step("Research Planner")
        plan = PlannerAgent.plan(request.query, request.mode)
        tracer.end_step("Research Planner", details={"sub_questions": len(plan.sub_questions)})

        # 2. Multi-Source Search & Retrieval Phase
        tracer.start_step("Multi-Source Retrieval")
        sources = await ResearcherAgent.collect_sources(plan, max_sources=request.max_sources)
        tracer.end_step("Multi-Source Retrieval", details={"sources_found": len(sources)})

        # 3. Document Chunking & Hybrid RRF Retrieval Phase
        tracer.start_step("Chunking & Hybrid RRF Retrieval")
        raw_chunks: List[EvidenceChunk] = []
        for s in sources:
            chunk = EvidenceChunk(
                id=f"chk_{uuid.uuid4().hex[:8]}",
                source_id=s.id,
                content=s.snippet,
                chunk_index=0
            )
            raw_chunks.append(chunk)

        rrf_retriever = HybridRRFRetriever(k=60)
        ranked_chunks = rrf_retriever.search(request.query, raw_chunks, top_k=min(15, len(raw_chunks)))
        tracer.end_step("Chunking & Hybrid RRF Retrieval", details={"ranked_chunks": len(ranked_chunks)})

        # 4. Atomic Claim Extraction Phase
        tracer.start_step("Atomic Claim Extraction")
        claims = ClaimExtractor.extract_claims(sources, ranked_chunks)
        tracer.end_step("Atomic Claim Extraction", details={"extracted_claims": len(claims)})

        # 5. Citation Verification Phase (4-Tier)
        tracer.start_step("4-Tier Citation Verification")
        verifier = CitationVerifier()
        citations = await verifier.verify_and_build_citations(claims, sources)
        tracer.end_step("4-Tier Citation Verification", details={"verified_citations": len(citations)})

        # 6. Research Synthesis Phase
        tracer.start_step("Report Synthesis")
        report = ResearchSynthesizer.synthesize_report(
            topic=request.query,
            plan=plan,
            claims=claims,
            citations=citations,
            mode=request.mode
        )
        tracer.end_step("Report Synthesis", details={"sections": len(report.sections)})

        # 7. Independent Critic & Fact-Checker Phase
        tracer.start_step("Critic Audit")
        critic_feedback = ResearchCritic.evaluate_report(report, plan)
        tracer.end_step("Critic Audit", details={"score": critic_feedback.score, "passed": critic_feedback.passes_audit})

        # 8. Evaluation & Metrics
        eval_metrics = ResearchEvaluator.evaluate_research(report, sources)

        # Assemble Full Trace
        full_trace = tracer.to_trace(
            total_sources=len(sources),
            total_claims=len(claims),
            total_citations=len(citations)
        )

        completed_at = datetime.now(timezone.utc)

        return ResearchRunResponse(
            id=run_id,
            query=request.query,
            mode=request.mode,
            status=RunStatus.COMPLETED,
            created_at=created_at,
            completed_at=completed_at,
            plan=plan,
            sources_count=len(sources),
            claims_count=len(claims),
            citations_count=len(citations),
            critic_score=critic_feedback.score,
            report=report,
            trace=full_trace
        )
