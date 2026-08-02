"""Direct LLM engine — RAG + chat-completions without CrewAI."""

import json
import re
from dataclasses import replace

from sqlalchemy.orm import Session

from ..models import Organization
from ..services import knowledge_service, usage
from ..services.llm import get_llm
from .engine import HandleResult
from . import fallback_engine

SYSTEM_PROMPT = (
    "You are a professional AI support assistant for '{company}'.\n"
    "Analyze the customer ticket below.\n"
    "Return ONLY a JSON object with exactly these keys:\n"
    '{{"classification": "<billing|account|technical|order|security|general>", '
    '"priority": "<low|medium|high|urgent>", '
    '"draft": "<your reply to the customer, 3-8 sentences, using the knowledge base>", '
    '"summary": "<one sentence internal summary>", '
    '"escalate": <true|false>}}\n'
    "Use the knowledge base excerpts. If the excerpt answers the question, answer it. "
    "Set escalate=true when the ticket is urgent, sensitive, or the knowledge base is insufficient."
)


def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def handle_ticket(
    db: Session,
    organization: Organization,
    subject: str,
    body: str,
    top_k: int = 4,
) -> HandleResult:
    hits = knowledge_service.search(db, organization.id, f"{subject} {body}", top_k=top_k)
    context = "\n\n".join(
        f"[{i + 1}] {hit['text']}" for i, hit in enumerate(hits)
    ) or "(no knowledge matches)"

    user_prompt = (
        f"Company: {organization.name}\n"
        f"Ticket subject: {subject}\n"
        f"Ticket body: {body}\n\n"
        f"Knowledge base excerpts:\n{context}"
    )

    llm = get_llm()
    try:
        result = llm.complete(SYSTEM_PROMPT.format(company=organization.name), user_prompt)
        parsed = _extract_json(result.text)
    except Exception:
        parsed = None
        result = None

    usage.track(
        db,
        organization_id=organization.id,
        kind="llm",
        model=getattr(llm, "model", None),
        tokens_in=result.usage.prompt_tokens if result else 0,
        tokens_out=result.usage.completion_tokens if result else 0,
        meta={"action": "ticket.handle"},
    )

    if parsed and parsed.get("draft"):
        return HandleResult(
            classification=str(parsed.get("classification", "general")),
            priority=str(parsed.get("priority", "medium")),
            draft=str(parsed["draft"]),
            summary=str(parsed.get("summary", "")),
            sources=[{"text": h["text"], "score": h["score"], "filename": h["filename"]} for h in hits],
            escalate=bool(parsed.get("escalate", False)),
            confidence=round(hits[0]["score"], 4) if hits else 0.5,
            engine="llm",
            notes="Draft generated with an LLM over tenant knowledge.",
        )

    # LLM failed or returned nothing useful → rule-based fallback
    fallback = fallback_engine.handle_ticket(db, organization, subject, body, top_k=top_k)
    return replace(fallback, notes="LLM output was unusable; used fallback engine.")
