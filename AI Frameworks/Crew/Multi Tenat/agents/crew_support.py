"""CrewAI hierarchical support crew.

Agent roster (configured per tenant in ``agent_configs``):

- Manager      — orchestrates the crew, delegates and reviews (hierarchical process)
- Router       — classifies the ticket and sets priority
- Knowledge    — pulls the most relevant tenant knowledge via the RAG tool
- Support      — drafts the customer reply grounded in that knowledge
- Escalation   — decides whether a human must take over
- Report       — writes the internal summary

Requires ``crewai`` installed (Python ≤ 3.13) and an LLM provider configured.
"""

from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Organization
from ..services import knowledge_service, usage
from ..services.llm import crew_llm_kwargs, get_llm
from .engine import HandleResult


class CrewResult(BaseModel):
    classification: str = Field(default="general")
    priority: str = Field(default="medium")
    draft: str = Field(default="")
    summary: str = Field(default="")
    escalate: bool = Field(default=False)


def _build_tool(organization_id: str):
    """Build the tenant-scoped knowledge retrieval tool (CrewAI BaseTool)."""
    from crewai.tools import BaseTool
    from ..core.database import SessionLocal

    class KnowledgeRetrievalTool(BaseTool):
        name: str = "Knowledge base search"
        description: str = (
            "Search this workspace's isolated knowledge base. "
            "Pass a natural-language question; returns relevant excerpts with scores."
        )

        def _run(self, argument: str) -> str:
            import json

            db: Session = SessionLocal()
            try:
                hits = knowledge_service.search(db, organization_id, argument, top_k=4)
            finally:
                db.close()
            return json.dumps(
                [
                    {
                        "text": hit["text"],
                        "score": hit["score"],
                        "source": hit["filename"],
                    }
                    for hit in hits
                ]
            )

    return KnowledgeRetrievalTool()


def build_crew(organization: Organization, subject: str, body: str):
    from crewai import Agent, Crew, Process, LLM, Task

    llm = LLM(**crew_llm_kwargs())
    tool = _build_tool(organization.id)

    manager = Agent(
        role="Support Manager",
        goal=(
            "Coordinate the crew to resolve the customer ticket accurately and safely, "
            "using the workspace knowledge base, and decide when a human must take over."
        ),
        backstory=(
            f"You lead the AI support crew for {organization.name}. You review each step, "
            "keep replies professional and escalate anything sensitive or unresolved."
        ),
        llm=llm,
        allow_delegation=True,
    )

    router = Agent(
        role="Ticket Router",
        goal="Classify the ticket into a category and set an appropriate priority.",
        backstory="You triage inbound tickets quickly and consistently.",
        llm=llm,
        allow_delegation=False,
    )

    knowledge_agent = Agent(
        role="Knowledge Agent",
        goal="Find the most relevant excerpts from the tenant knowledge base.",
        backstory="You are precise and only rely on retrieved evidence.",
        tools=[tool],
        llm=llm,
        allow_delegation=False,
    )

    support_agent = Agent(
        role="Support Agent",
        goal="Draft a clear, friendly, accurate reply using the retrieved knowledge.",
        backstory="You write empathetic, professional support replies grounded in facts.",
        tools=[tool],
        llm=llm,
        allow_delegation=False,
    )

    escalation_agent = Agent(
        role="Escalation Agent",
        goal="Decide if this ticket needs a human (urgency, sensitivity, low confidence).",
        backstory="You protect the customer by routing the right work to humans.",
        llm=llm,
        allow_delegation=False,
    )

    report_agent = Agent(
        role="Report Agent",
        goal="Write a one-sentence internal summary of the handling.",
        backstory="You summarize outcomes for the team's dashboard.",
        llm=llm,
        allow_delegation=False,
    )

    ticket = f"Subject: {subject}\nCustomer message: {body}"

    tasks = [
        Task(
            description=f"Classify this ticket.\n{ticket}",
            expected_output="A single category (billing|account|technical|order|security|general) and priority (low|medium|high|urgent).",
            agent=router,
        ),
        Task(
            description="Find up to 3 relevant knowledge excerpts for this ticket.",
            expected_output="The best matching excerpts and their relevance.",
            agent=knowledge_agent,
        ),
        Task(
            description="Write the customer-facing reply using the retrieved knowledge.",
            expected_output="A polished 3-8 sentence reply. Never invent facts not present in the knowledge base.",
            agent=support_agent,
        ),
        Task(
            description="Decide whether a human must handle this ticket.",
            expected_output="true or false with a short reason.",
            agent=escalation_agent,
        ),
        Task(
            description="Summarize the ticket and the chosen resolution.",
            expected_output="A one-sentence internal summary.",
            agent=report_agent,
        ),
    ]

    return Crew(
        agents=[router, knowledge_agent, support_agent, escalation_agent, report_agent],
        tasks=tasks,
        process=Process.hierarchical,
        manager_agent=manager,
        verbose=False,
    )


def handle_ticket(
    db: Session,
    organization: Organization,
    subject: str,
    body: str,
    top_k: int = 4,
) -> HandleResult:
    from ..services.vector import get_vector_store
    from . import fallback_engine

    try:
        from crewai import Crew

        crew = build_crew(organization, subject, body)
        if not isinstance(crew, Crew):
            raise RuntimeError("crew build failed")
        output = crew.kickoff()

        hits = knowledge_service.search(db, organization.id, f"{subject} {body}", top_k=top_k)
        usage.track(
            db,
            organization_id=organization.id,
            kind="flow",
            model=settings.LLM_MODEL,
            meta={"action": "crew.ticket.handle", "agents": 6},
        )

        parsed: Optional[CrewResult] = None
        if output is not None:
            parsed = getattr(output, "pydantic", None) or (
                output if isinstance(output, CrewResult) else None
            )

        if parsed and parsed.draft:
            return HandleResult(
                classification=parsed.classification,
                priority=parsed.priority,
                draft=parsed.draft,
                summary=parsed.summary,
                sources=[{"text": h["text"], "score": h["score"], "filename": h["filename"]} for h in hits],
                escalate=parsed.escalate,
                confidence=round(hits[0]["score"], 4) if hits else 0.5,
                engine="crewai",
                notes="Handled by a hierarchical CrewAI crew (Manager + 5 agents).",
            )

        # Crew ran but produced no parseable structured result → fall back.
        return fallback_engine.handle_ticket(db, organization, subject, body, top_k=top_k)
    except Exception as exc:
        notes = f"CrewAI unavailable or errored ({exc}); used fallback engine."
        result = fallback_engine.handle_ticket(db, organization, subject, body, top_k=top_k)
        result.notes = notes
        return result
