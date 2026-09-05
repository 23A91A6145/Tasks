import uuid
from typing import List
from backend.app.models.schemas import ResearchPlan, SubQuestion
from backend.app.core.constants import ResearchMode, SourceType

class ResearchPlanner:
    """Decomposes high-level research questions into orthogonal sub-questions and query sets."""

    @staticmethod
    def generate_plan(topic: str, mode: ResearchMode) -> ResearchPlan:
        sub_questions: List[SubQuestion] = []
        clean_topic = topic.strip()

        # Vector 1: Architectural Foundations
        sub_questions.append(
            SubQuestion(
                id=f"sq_{uuid.uuid4().hex[:6]}",
                question=f"What are the core architectural foundations and design patterns of {clean_topic}?",
                rationale="Establishes structural mechanisms, state primitives, and communication topologies.",
                search_queries=[
                    f"{clean_topic} architecture state machine checkpointing",
                    f"{clean_topic} design patterns orchestration graph"
                ],
                target_sources=[SourceType.DOCUMENTATION, SourceType.ACADEMIC]
            )
        )

        # Vector 2: State Persistence & Fault Tolerance
        sub_questions.append(
            SubQuestion(
                id=f"sq_{uuid.uuid4().hex[:6]}",
                question=f"How does {clean_topic} handle persistence, fault tolerance, and human-in-the-loop controls?",
                rationale="Evaluates durability, resumption after failure, and human governance.",
                search_queries=[
                    f"{clean_topic} persistence PostgreSQL memory checkpointing",
                    f"{clean_topic} human-in-the-loop interrupts fault tolerance"
                ],
                target_sources=[SourceType.DOCUMENTATION, SourceType.WEB]
            )
        )

        # Vector 3: Empirical Benchmarks & Production Performance
        sub_questions.append(
            SubQuestion(
                id=f"sq_{uuid.uuid4().hex[:6]}",
                question=f"What are the empirical benchmarks, latency, token costs, and scaling limits for {clean_topic}?",
                rationale="Identifies real-world operational trade-offs and performance ceilings.",
                search_queries=[
                    f"{clean_topic} benchmark latency token consumption scale",
                    f"{clean_topic} production case study performance evaluation"
                ],
                target_sources=[SourceType.ACADEMIC, SourceType.WEB]
            )
        )

        # Vector 4: Ecosystem, Tooling & Future Demand
        sub_questions.append(
            SubQuestion(
                id=f"sq_{uuid.uuid4().hex[:6]}",
                question=f"What is the ecosystem integration, MCP compatibility, and future demand curve for {clean_topic} in 2026?",
                rationale="Gauges developer adoption, enterprise longevity, and tool protocols.",
                search_queries=[
                    f"{clean_topic} Model Context Protocol MCP integration 2026",
                    f"{clean_topic} enterprise adoption developer ecosystem"
                ],
                target_sources=[SourceType.WEB, SourceType.DOCUMENTATION]
            )
        )

        total_searches = sum(len(sq.search_queries) for sq in sub_questions)
        estimated_sec = 25 if mode == ResearchMode.QUICK else 60

        return ResearchPlan(
            topic=clean_topic,
            objective=f"Produce an authoritative, citation-verified technical investigation into {clean_topic}.",
            sub_questions=sub_questions,
            planned_searches=total_searches,
            estimated_time_seconds=estimated_sec
        )
